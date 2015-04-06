import pygame
import spriteObject
import settingsManager

class Stage():
    def __init__(self):
        #Platforms are static, non-moving interactables.
        #They are never updated after creation, to save on memory.
        
        
        #Entities are updated whenever the frame is drawn.
        #If it changes at all on the stage, it is an entity
        self.entity_list = []
        
        #self.size = pygame.Rect(0,0,1080,720)
        self.size = pygame.Rect(0,0,2160,1440)
        
        #self.camera_maximum = pygame.Rect(24,16,1032,688)
        self.camera_maximum = pygame.Rect(48,32,2064,1376)
        
        #self.blast_line = pygame.Rect(0,0,1080,720)
        self.blast_line = pygame.Rect(0,0,2160,1440)
        
        self.camera_position = pygame.Rect(24,16,settingsManager.getSetting('windowWidth'),settingsManager.getSetting('windowHeight'))
        self.camera_position.midtop = self.size.midtop
        
        self.camera_preferred_position = pygame.Rect(24,16,settingsManager.getSetting('windowWidth'),settingsManager.getSetting('windowHeight'))
        self.camera_preferred_position.midtop = self.size.midtop
        
        self.follows = []
        self.active_hitboxes = pygame.sprite.Group()
        
        #self.centerSprite = spriteObject.RectSprite([0,0],[32,32])
        self.deadZone = [64,32]
        
        self.platform_list = [spriteObject.RectSprite([552,824],[798,342])]
        #self.platform_list = [spriteObject.RectSprite([138,412],[798,342])]
        
        self.sprite = spriteObject.ImageSprite("fd",[494,790],generateAlpha=False,file = __file__)
        
        self.preferred_zoomLevel = 1.0
        self.zoomLevel = 1.0
        
    def update(self):
        for entity in self.entity_list:
            entity.update()
        if self.preferred_zoomLevel != self.zoomLevel:
            diff = self.zoomLevel - self.preferred_zoomLevel
            if diff > 0: #If the camera is too narrow
                self.zoomLevel -= min([0.1,diff])
            else:
                self.zoomLevel += min([0.1,-diff])
            self.camera_position.width  = round(float(settingsManager.getSetting('windowWidth'))  * self.zoomLevel)
            self.camera_position.height = round(float(settingsManager.getSetting('windowHeight')) * self.zoomLevel)
        if self.camera_position.x != self.camera_preferred_position.x:
            diff = self.camera_position.x - self.camera_preferred_position.x
            if diff > 0: #If the camera is too far to the right
                self.camera_position.x -= min([10,diff]) #otherwise, move 10 pixels closer
            else: #If the camera is too far to the left
                self.camera_position.x += min([10,-diff])
        if self.camera_position.y != self.camera_preferred_position.y:
            diff = self.camera_position.y - self.camera_preferred_position.y
            if diff > 0: #If the camera is too far to the bottom
                self.camera_position.y -= min([20,diff])
            else: #If the camera is too far to the top
                self.camera_position.y += min([20,-diff])
        
    def centerCamera(self,center):
        self.camera_preferred_position.width  = round(settingsManager.getSetting('windowWidth')  * self.preferred_zoomLevel)
        self.camera_preferred_position.height = round(settingsManager.getSetting('windowHeight') * self.preferred_zoomLevel)
        self.camera_preferred_position.center = center
        
        if self.camera_preferred_position.left < self.camera_maximum.left: self.camera_preferred_position.left = self.camera_maximum.left
        if self.camera_preferred_position.right > self.camera_maximum.right: self.camera_preferred_position.right = self.camera_maximum.right
        if self.camera_preferred_position.top < self.camera_maximum.top:
            self.camera_preferred_position.top = self.camera_maximum.top
        if self.camera_preferred_position.bottom > self.camera_maximum.bottom: self.camera_preferred_position.bottom = self.camera_maximum.bottom
        
        
    #If Center is not given, will shift the camera by the given x and y
    #If Center is True, will center the camera on the given x and y
    def moveCamera(self,x,y,center=False):
        if center:
            newRect = self.camera_preferred_position.copy()
            newRect.center = [x,y]
        else:
            newRect = self.camera_preferred_position.copy()
            newRect.x += x
            newRect.y += y
        self.camera_preferred_position = newRect
        
        
    def draw(self,screen):
        for plat in self.platform_list: plat.draw(screen,self.stageToScreen(plat.rect),self.getScale())        
        self.sprite.draw(screen,self.stageToScreen(self.sprite.rect),self.getScale())
        #self.centerSprite.draw(screen, self.stageToScreen(self.centerSprite.rect), self.getScale())

    def cameraUpdate(self):
        leftmost = self.follows[0]
        rightmost = self.follows[0]
        topmost = self.follows[0]
        bottommost = self.follows[0]
        for obj in self.follows:
            if obj.left < leftmost.left:
                leftmost = obj
            if obj.right > rightmost.right:
                rightmost = obj
            if obj.top < topmost.top:
                topmost = obj
            if obj.bottom > bottommost.bottom:
                bottommost = obj
        xdist = (rightmost.right - leftmost.left) + (2*self.deadZone[0])
        ydist = (bottommost.bottom - topmost.top) + (2*self.deadZone[1])
        
        xZoom = xdist / float(settingsManager.getSetting('windowWidth'))
        yZoom = ydist / float(settingsManager.getSetting('windowHeight'))
        
        if xZoom < 1.0: xZoom = 1.0
        if yZoom < 1.0: yZoom = 1.0
        
        if xZoom * settingsManager.getSetting('windowWidth') > self.camera_maximum.width:
            xZoom = self.camera_maximum.width / float(settingsManager.getSetting('windowWidth'))
        if yZoom * settingsManager.getSetting('windowHeight') > self.camera_maximum.height:
            yZoom = self.camera_maximum.height / float(settingsManager.getSetting('windowHeight'))
        
        self.preferred_zoomLevel = max([xZoom,yZoom])
        if self.preferred_zoomLevel > (self.camera_maximum.width/float(settingsManager.getSetting('windowWidth'))):
            self.preferred_zoomLevel = self.camera_maximum.width/float(settingsManager.getSetting('windowWidth'))
        if self.preferred_zoomLevel > (self.camera_maximum.height/float(settingsManager.getSetting('windowHeight'))):
            self.preferred_zoomLevel = self.camera_maximum.height/float(settingsManager.getSetting('windowHeight'))
    
        boundingBox = pygame.Rect(leftmost.left-self.deadZone[0],topmost.top-self.deadZone[1],xdist,ydist)
        center = boundingBox.center
        
        self.centerCamera(center)
        
    def stageToScreen(self,rect):
        x = rect.x - self.camera_position.x
        y = rect.y - self.camera_position.y
        return (x,y)
    
    def getScale(self):
        h = round(float(settingsManager.getSetting('windowHeight')) / self.camera_position.height,5)
        w = round(float(settingsManager.getSetting('windowWidth')) / self.camera_position.width,5)
        
        if h == w:
            return h
        else:
            if abs(h - w) <= 0.02:
                return h
            print "Scaling Error", h, w, abs(h-w)
            return w