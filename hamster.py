from direct.showbase.DirectObject import DirectObject
from direct.showbase.InputStateGlobal import inputState
from direct.motiontrail.MotionTrail import MotionTrail
from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import Vec3, Point3, BitMask32, Vec4, InputDevice,TransparencyAttrib,TextureAttrib, TextureStage
from panda3d.bullet import BulletRigidBodyNode, BulletSphereShape


class Hamster(DirectObject):
    
    def __init__(self):
        super().__init__()
        self.last_mouse_x = 0
        self.last_mouse_y = 0
        self.jump_power = 9
        self.ground_normal = Vec3(0, 0, 0)
        self._setup_camera()
        self._setup_sound()
        self._subscribe_to_events()
        self._setup_rigid_bodies()
        self._setup_particles()

    def _setup_particles(self):
        self.smoke = ParticleEffect()
        self.smoke.loadConfig("particles/smoke.ptf")
        # orientation_trail = MotionTrail("fire trail", self.sphere)
        # orientation_trail.register_motion_trail()
        # orientation_trail.geom_node_path.reparent_to(base.render)
        # #orientation_trail.set_texture(loader.load_texture("particles/plasma.png"))
        # orientation_trail.time_window = .6 # Length of trail
        # orientation_trail.add_vertex(Point3(0, 0, 1))
        # orientation_trail.add_vertex(Point3(0, 0,-1))
        # orientation_trail.set_vertex_color(0, Vec4(0,1, 0, 1),Vec4(0,1, 0, 1))
        # orientation_trail.set_vertex_color(1, Vec4(0,1, 0, 1),Vec4(0,1, 0, 1))
        # orientation_trail.update_vertices()

    def _setup_sound(self):
        self.jump_sound = base.loader.loadSfx("sound/fx/jump.wav")
        self.skid_sound = base.loader.loadSfx("sound/fx/skid.wav")
        self.bounce_sound = base.loader.loadSfx("sound/fx/bounce.wav")
        self.skid_sound.setVolume(0.3)
        self.skid_sound.setLoop(True)

    def _check_ground(self, task):
        result = base.bullet_world.contactTest(self.sphere.node())
        if result.getNumContacts() > 0:
            contact = result.getContacts()[0]
            mpoint = contact.getManifoldPoint()
            if self.ground_normal == Vec3(0,0,0) and abs(self.sphere.node().getLinearVelocity().length()) > 8:
                self.bounce_sound.play()
            self.ground_normal = mpoint.getNormalWorldOnB()
        else:
           self.ground_normal = Vec3(0, 0, 0)
        return task.cont

    def _process_input(self, dt):
        # Access and use the value for whatever you need it
        torque = Vec3(0, 0, 0)
        force = Vec3(0, 0, 0)
        
        if base.gamepad:
            left_x = base.gamepad.findAxis(InputDevice.Axis.left_x)
            left_y = base.gamepad.findAxis(InputDevice.Axis.left_y)
            gp_torque = Vec3(0,0,0)
            gp_force = Vec3(0,0,0)
            if abs(left_x.value) > 0.1:
                gp_torque.y = left_x.value 
                gp_force.x = left_x.value
            if abs(left_y.value) > 0.1:
                gp_torque.x = left_y.value * -1
                gp_force.y = left_y.value

            torque = gp_torque
            force = gp_force

        else:
            if inputState.isSet('forward') : 
                torque.setX(-1.0)
                force.setY(1.0)
            if inputState.isSet('reverse'):
                torque.setX(1.0)
                force.setY(-1.0)
            if inputState.isSet('left'):   
                torque.setY(-1.0)
                force.setX(-1.0)
            if inputState.isSet('right'):   
                torque.setY(1.0)
                force.setX(1.0)

        torque *= 8
        force *= 8

        torque = render.getRelativeVector(self.gimbal_x, torque)
        force = render.getRelativeVector(self.gimbal_x, force)
        self.sphere.node().setActive(True)
        
        self.sphere.node().applyTorque(torque)
        self.sphere.node().applyForce(force, Point3(0,0, 0))

        if inputState.isSet('break'):
            self.slow()
        else:
            if self.skid_sound.status() == self.skid_sound.PLAYING:
                self.skid_sound.stop()  

    def _subscribe_to_events(self):
        inputState.watchWithModifiers('forward', 'w')
        inputState.watchWithModifiers('left', 'a')
        inputState.watchWithModifiers('reverse', 's')
        inputState.watchWithModifiers('right', 'd')
        inputState.watchWithModifiers('break', 'e')
        inputState.watchWithModifiers('break', 'controller-face_x')
        inputState.watchWithModifiers('break', 'controller-lshoulder')
        self.accept("space", self.jump)
        self.accept("r", self.reset)
        self.accept("controller-face_a", self.jump)
        self.accept("controller-face_b", self.reset)
        self.accept("wheel_up", self._zoom_in)
        self.accept("wheel_down", self._zoom_out)

    def _stop_particle(self, task):
        self.smoke.disable()
        return task.done
        

    def slow(self):
        self.sphere.node().setAngularVelocity(0)
        if self.ground_normal != Vec3(0,0,0):
            if abs(self.sphere.node().getLinearVelocity().length()) > 12:
                if self.skid_sound.status() != self.skid_sound.PLAYING:
                    self.skid_sound.play()
                self.smoke.start(parent = base.render, renderParent = base.render)
                self.smoke.setPos(self.sphere.getPos() + Vec3(0,0,-1))
                base.taskMgr.doMethodLater(1, self._stop_particle, "smoke stop")
            else:
                if self.skid_sound.status() == self.skid_sound.PLAYING:
                    self.skid_sound.stop()



            

    def reset(self):
        self.sphere.setPos(0,0,0)

    def jump(self):
        if self.ground_normal != Vec3(0,0,0):
            self.jump_sound.play()
            self.sphere.node().applyImpulse(self.ground_normal * self.jump_power, Point3(0,0,0))
        else:
            self.jump_sound.stop()

    def _setup_camera(self):
        base.disableMouse()
        base.taskMgr.add(self._handle_orbit_gimbal)
        base.taskMgr.add(self._self_follow)
        self.gimbal_x = base.render.attachNewNode("gimbal_x")
        self.gimbal_y = self.gimbal_x.attachNewNode("gimbal_y")
        base.camera.reparentTo(self.gimbal_y)
        base.camera.setY(-20)

    def _zoom_in(self):
        if base.camera.getY() > -10.0:
            return
        base.camera.setY(base.camera, 5)
        

    def _zoom_out(self):
        if base.camera.getY() < -50.0:
            return
        base.camera.setY(base.camera, -5)

    def _handle_orbit_gimbal(self, task):
        if base.gamepad:
            x = base.gamepad.findAxis(InputDevice.Axis.right_x)
            y = base.gamepad.findAxis(InputDevice.Axis.right_y)
            if abs(x.value) > 0.1:
                self.gimbal_x.setH(self.gimbal_x, -(x.value * 100 * globalClock.get_dt()))
            if abs(y.value) > 0.1:
                self.gimbal_y.setP(self.gimbal_y, -(y.value * 100 * globalClock.get_dt()))
            return task.cont

        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX()
            y = base.mouseWatcherNode.getMouseY()
            delta_x = self.last_mouse_x - x
            delta_y = self.last_mouse_y - y
            self.last_mouse_x = x
            self.last_mouse_y = y
            self.gimbal_x.setH(self.gimbal_x, delta_x * 10000 * globalClock.get_dt())
            self.gimbal_y.setP(self.gimbal_y, -(delta_y * 10000 * globalClock.get_dt()))
        
        return task.cont
    
    def _self_follow(self, task):
        ballPos = self.sphere.getPos()
        self.gimbal_x.setPos(ballPos)
        base.sunnp.setPos(ballPos + Vec3(0, 0, 2))
        return task.cont
    
    def _setup_rigid_bodies(self):
        sphere_shape = BulletSphereShape(1)

        self.sphere = base.bullet_world_node_path.attachNewNode(BulletRigidBodyNode('ball'))
        self.sphere.node().setMass(1)
        self.sphere.node().setFriction(1)
        self.sphere.node().addShape(sphere_shape)
        self.sphere.setPos(0, 0, 2)
        self.sphere.setCollideMask(BitMask32.allOn())
        self.sphere.node().setRestitution(.1)
        base.bullet_world.attachRigidBody(self.sphere.node())

        hamster = loader.loadModel('models/hammy.egg')
        
        hamster.reparentTo(self.sphere)
        hamster.setScale(0.1)
        hamster.setH(180)
        visual_sphere = loader.loadModel('models/sphere.egg')
        visual_sphere.setShaderOff()
        visual_sphere.reparentTo(self.sphere)
        visual_sphere.setTransparency(1)
        visual_sphere.setBin("transparent",0)

        visual_sphere.setColorScale(1,1,1,.6)
        visual_sphere.setLightOff()
        mat = hamster.findMaterial("body")
        mat.setBaseColor((0,1,1,1))
        base.taskMgr.add(self.update)
        base.taskMgr.add(self._check_ground, sort=-1)

    def update(self, task):
        dt = globalClock.getDt()
        self._process_input(dt)
        return task.cont