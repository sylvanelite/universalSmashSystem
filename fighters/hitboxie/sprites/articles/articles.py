import engine.article as article
import engine.hitbox as hitbox
import math
import pygame

class SplatArticle(article.AnimatedArticle):
    def __init__(self, owner):
        origin = (owner.sprite.boundingRect.centerx + (24 * owner.facing), owner.sprite.boundingRect.centery)
        article.AnimatedArticle.__init__(self, owner.article_path+'/hitboxie_projectile.png', owner, origin, imageWidth=16,length=120)
        
        self.direction = owner.facing
        self.change_x = self.direction*24
        self.change_y = 0
        
        variables = {'center':[0,0],
                     'size':[12,12],
                     'damage':3,
                     'baseKnockback':2,
                     'knockbackGrowth':0,
                     'trajectory':0,
                     'hitstun':1,
                     'transcendence':-1
                     }
        self.hitbox = hitbox.DamageHitbox(self.owner, hitbox.HitboxLock(), variables)
        
        self.hitbox.article = self
        self.hitbox.owner = self.owner
        
        self.tags = ['reflectable']

    # Override the onCollision of the hitbox
    def onCollision(self, other):
        othersClasses = list(map(lambda x :x.__name__,other.__class__.__bases__)) + [other.__class__.__name__]
        if ('AbstractFighter' in othersClasses or 'Platform' in othersClasses):
            self.deactivate()
        #TODO check for verticality of platform landing
            
    def update(self):
        self.rect.x += self.change_x
        self.rect.y += self.change_y
        self.change_y += 0.5
        self.hitbox.update()
        self.frame += 1
        self.angle = -math.atan2(self.change_y, self.change_x)*180.0/math.pi
            
        if self.frame > 120:
            self.kill()
            self.hitbox.kill()
    
    def activate(self):
        article.AnimatedArticle.activate(self)
        self.rect.center = (self.owner.sprite.boundingRect.centerx + (24 * self.owner.facing),self.owner.sprite.boundingRect.centery-8)
        self.owner.active_hitboxes.add(self.hitbox)
    
    def deactivate(self):
        article.AnimatedArticle.deactivate(self)
        self.hitbox.kill()
        self.kill()

class ShineArticle(article.AnimatedArticle):
    def __init__(self, owner):
        article.AnimatedArticle.__init__(self, owner.article_path+'/hitboxie_shine.png', owner, [0,0], imageWidth=92,length=8)
            
    def update(self):
        self.rect.center = self.owner.sprite.boundingRect.center
        if self.frame == 0:
            self.getImageAtIndex(0)
        elif self.frame == 2:
            self.getImageAtIndex(1)
        elif self.frame == 4:
            self.getImageAtIndex(2)
        elif self.frame == 6:
            self.getImageAtIndex(3)
        if self.frame == self.lastFrame:
            self.frame = 2
        else:
            self.frame += 1
