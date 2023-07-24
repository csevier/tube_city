from hamster import Hamster
from direct.showbase.InputStateGlobal import inputState
from fix_gltf_bam import render_stage_convert
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import TextureStage, TexGenAttrib
from panda3d.core import (
                         AmbientLight, 
                         DirectionalLight,
                         )

class Level(DirectObject):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self._load()
        #self._debug_bullet()


    def load(self):
        self._load_assets()
        self._set_up_environment_lighting()
        self._set_up_skybox()
        self._associate_obstacles()
        self._setup_initial_tasks()
        self._start_music()
        self._setup_controller()
        self._load_player()
        self._put_in_scene_graph()

    def _remove_from_scene_graph(self):
        self.playground.removeNode()
        self.skybox.removeNode()

    def unload(self):
        #unhook events etc.
        self._stop_music()
        self._remove_from_scene_graph()

    def _load_player(self):
        self.hamster = Hamster()

    def _load_assets(self):
        self.background_music = base.loader.loadSfx("sound/songs/Zane Little - Dizzy Racing.ogg")
        self.skybox = base.loader.loadModel("models/inverted_sphere.egg")
        self.cubemap = base.loader.loadCubeMap("skyboxes/cloud/#.jpg")
        self.playground = base.loader.loadModel(self.name)

    def _associate_obstacles(self):
        render_stage_convert(self.playground, use_modulate = True, use_normal = False, use_selector = False, use_emission = False)
        for node_path in self.playground.find_all_matches('**/+BulletRigidBodyNode'):
           node_path.node().setMass(0)
           node_path.node().setFriction(2)
           node_path.node().setRestitution(2)
           base.bullet_world.attachRigidBody(node_path.node())

    def _put_in_scene_graph(self):
        self.skybox.reparentTo(base.render)
        self.playground.reparentTo(base.bullet_world_node_path)

    def _start_music(self):
        self.background_music.setVolume(0.09)
        self.background_music.setLoop(True)
        self.background_music.play()

    def _stop_music(self):
        self.background_music.stop()

    def _setup_controller(self):
        try:
            base.gamepad = base.devices.getDevices(InputDevice.DeviceClass.gamepad)[0]
            base.attachInputDevice(base.gamepad, prefix="controller")
        except:
            base.gamepad = None
            print("No gamepad found.")
        
    def _set_up_environment_lighting(self):
        self.sun = DirectionalLight("sun")
        self.sun.setColor((1, 1, 1, 1))
        base.sunnp = base.render.attachNewNode(self.sun)
        base.sunnp.setZ(base.sunnp, 50)
        base.sunnp.setY(base.sunnp, -30)
        base.sunnp.setP(base.sunnp, -90)
        base.sunnp.node().setShadowCaster(True, 512, 512)
        base.sunnp.node().getLens().setFilmSize(2,2)
        base.render.setLight(base.sunnp)
        self.ambient_light = AmbientLight('alight')
        self.ambient_light.setColor((0.8,0.8,0.8, 1))
        self.alnp = base.render.attachNewNode(self.ambient_light)
        base.render.setLight(self.alnp)

    def _set_up_skybox(self):
        self.skybox.setTexGen(TextureStage.getDefault(), TexGenAttrib.MWorldPosition)
        self.skybox.setTexProjector(TextureStage.getDefault(), base.render, self.skybox)
        self.skybox.setTexture(self.cubemap)
        self.skybox.setLightOff()
        self.skybox.setDepthWrite(True)
        self.skybox.setAlphaScale(0)
        self.skybox.setScale(1500)
    
    def _setup_initial_tasks(self):
        base.taskMgr.add(self.update, sort=-2, name = f"update_{self.name}")

    def update(self, task):
        dt = globalClock.getDt()
        base.bullet_world.doPhysics(dt, 5, 1.0/180.0)
        return task.cont