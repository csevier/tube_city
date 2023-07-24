from direct.showbase.ShowBase import ShowBase
from direct.filter.CommonFilters import CommonFilters
from level import Level
from panda3d.bullet import (BulletDebugNode, 
                            BulletWorld)

from panda3d.core import (loadPrcFileData, 
                         WindowProperties,
                         LightRampAttrib,
                         Vec3
                         )

import sys
loadPrcFileData("", "show-frame-rate-meter #t")
loadPrcFileData("", "sync-video #t")
loadPrcFileData("", "frame-rate-meter-milliseconds true")
loadPrcFileData("", "show-scene-graph-analyzer-meter true")

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        props = WindowProperties()
        props.setSize((1920,1080))
        props.setTitle("tube_city")
        props.setCursorHidden(True)
        props.setMouseMode(WindowProperties.M_relative)
        base.win.requestProperties(props)
        base.enableParticles()
        base.render.setShaderAuto()
        base.render.setAttrib(LightRampAttrib.makeSingleThreshold(0.2,1.8))
        self._set_up_toon_shading()
        self._set_up_physics()
        self.accept("q", self.exit)
        self.accept("controller-face_start", self.exit)
        self.accept("p", self._toggle_physics_debug)
        #Level("levels/tube2.bam")
        Level("levels/playground.bam")

    def _toggle_physics_debug(self):
        if not base.debugNP.isHidden():
            base.debugNP.hide()
        else:
            base.debugNP.show()

    def exit(self):
        sys.exit()

    def _set_up_toon_shading(self):
        self.separation = 1.2  # Pixels
        self.filters = CommonFilters(base.win, base.cam)
        filterok = self.filters.setCartoonInk(separation=self.separation)
        if (filterok == False):
            print(
                "Toon Shader: Video card not powerful enough to do image postprocessing")
            return
        
    def _set_up_physics(self):
        base.bullet_world_node_path = base.render.attachNewNode('World')
        base.bullet_world = BulletWorld()
        base.bullet_world.setGravity(Vec3(0, 0, -14)) # (0,0,-14)
        self._debug_bullet()

    
    def _debug_bullet(self):
        base.debugNode = BulletDebugNode('Debug')
        base.debugNode.showWireframe(True)
        base.debugNode.showConstraints(True)
        base.debugNode.showBoundingBoxes(True)
        base.debugNode.showNormals(True)
        base.debugNP = base.render.attachNewNode(base.debugNode)
        base.bullet_world.setDebugNode(base.debugNP.node())


app = MyApp()
app.run()