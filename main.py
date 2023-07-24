from direct.showbase.ShowBase import ShowBase, TextureStage, TexGenAttrib
from direct.filter.CommonFilters import CommonFilters
from direct.showbase.InputStateGlobal import inputState
from robotnik import collision_to_rigidbody
from fix_gltf_bam import render_stage_convert
from panda3d.core import (loadPrcFileData, 
                         WindowProperties, 
                         AmbientLight, 
                         DirectionalLight,
                         PointLight, 
                         LightRampAttrib, 
                         Vec3, 
                         BitMask32, 
                         CollisionBox, 
                         CollisionSphere,
                         CollisionCapsule, 
                         CollisionPlane,
                         CollisionPolygon,
                         InputDevice,
                         MaterialAttrib)
from panda3d.bullet import (BulletDebugNode, 
                            BulletWorld, 
                            BulletPlaneShape, 
                            BulletBoxShape, 
                            BulletRigidBodyNode, 
                            BulletSphereShape,
                            BulletCapsuleShape,
                            BulletTriangleMeshShape,
                            BulletHeightfieldShape,
                            BulletTriangleMesh)
from hamster import Hamster
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
        self._set_up_environment_lighting()
        self._set_up_skybox()
        self._set_up_toon_shading()
        self._setup_level()
        self._setup_music()
        self.accept("q", self.exit)
        
        self.hamster = Hamster()
        self._setup_controller()
        self.accept("controller-face_start", self.exit)
        base.enableParticles()
        #self._debug_bullet()

    def _setup_music(self):
        self.background_music = base.loader.loadSfx("sound/songs/Zane Little - Dizzy Racing.ogg")
        self.background_music.setVolume(0.2)
        self.background_music.setLoop(True)
        self.background_music.play()
    
    def _setup_controller(self):
        try:
            base.gamepad = base.devices.getDevices(InputDevice.DeviceClass.gamepad)[0]
            base.attachInputDevice(base.gamepad, prefix="controller")
        except:
            base.gamepad = None
            print("No gamepad found.")

    def exit(self):
        sys.exit()

    def _set_up_toon_shading(self):
        self.separation = 1.2  # Pixels
        self.filters = CommonFilters(self.win, self.cam)
        filterok = self.filters.setCartoonInk(separation=self.separation)
        if (filterok == False):
            print(
                "Toon Shader: Video card not powerful enough to do image postprocessing")
            return
    
    def _set_up_environment_lighting(self):
        base.render.setShaderAuto()
        base.render.setAttrib(LightRampAttrib.makeSingleThreshold(0.2,1.8))
        self.sun = DirectionalLight("sun")
        self.sun.setColor((1, 1, 1, 1))
        base.sunnp = self.render.attachNewNode( self.sun)
        base.sunnp.setZ(base.sunnp, 50)
        base.sunnp.setY(base.sunnp, -30)
        base.sunnp.setP(base.sunnp, -90)
        base.sunnp.node().setShadowCaster(True, 512, 512)
        base.sunnp.node().getLens().setFilmSize(2,2)
        base.render.setLight(base.sunnp)
        self.ambient_light = AmbientLight('alight')
        self.ambient_light.setColor((0.8,0.8,0.8, 1))
        self.alnp = self.render.attachNewNode(self.ambient_light)
        self.render.setLight(self.alnp)
    
    def _set_up_skybox(self):
        self.skybox = self.loader.loadModel("models/inverted_sphere.egg")
        self.cubemap = self.loader.loadCubeMap("skyboxes/cloud/#.jpg")
        self.skybox.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.skybox.setTexProjector(TextureStage.getDefault(), self.render, self.skybox)
        self.skybox.setTexture(self.cubemap)
        self.skybox.setLightOff()
        self.skybox.setDepthWrite(True)
        self.skybox.setAlphaScale(0)
        self.skybox.setScale(1500)
        self.skybox.reparentTo(self.render)

    def _debug_bullet(self):
        debugNode = BulletDebugNode('Debug')
        debugNode.showWireframe(True)
        debugNode.showConstraints(True)
        debugNode.showBoundingBoxes(True)
        debugNode.showNormals(True)
        debugNP = render.attachNewNode(debugNode)
        debugNP.show()
        base.bullet_world.setDebugNode(debugNP.node())
        

    def _setup_level(self):
        base.bullet_world_node_path = self.render.attachNewNode('World')
        base.bullet_world = BulletWorld()
        base.bullet_world.setGravity(Vec3(0, 0, -14)) # (0,0,-14)
        playground = loader.loadModel("levels/playground.bam")
        render_stage_convert(playground, use_modulate = True, use_normal = False, use_selector = False, use_emission = False)
        for node_path in playground.find_all_matches('**/+BulletRigidBodyNode'):
           node_path.node().setMass(0)
           node_path.node().setFriction(2)
           node_path.node().setRestitution(2)
           base.bullet_world.attachRigidBody(node_path.node())
        playground.reparentTo(base.bullet_world_node_path)
       
        #collision_to_rigidbody(base.bullet_world, playground)
        self.taskMgr.add(self.update, sort=-2)

    def update(self, task):
        dt = globalClock.getDt()
        base.bullet_world.doPhysics(dt, 5, 1.0/180.0)
        return task.cont

app = MyApp()
app.run()