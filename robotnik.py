from panda3d.core import (CollisionBox, 
                         CollisionSphere,
                         CollisionCapsule, 
                         CollisionPlane,
                         CollisionPolygon,
                         BitMask32
                         )
from panda3d.bullet import (BulletPlaneShape, 
                            BulletBoxShape, 
                            BulletRigidBodyNode, 
                            BulletSphereShape,
                            BulletCapsuleShape,
                            BulletTriangleMeshShape,
                            BulletHeightfieldShape,
                            BulletGhostNode,
                            BulletTriangleMesh,
                            )

def collision_to_rigidbody(bullet_world, node_path):
    collision_nodes = node_path.findAllMatches("**/+CollisionNode")
    for collision in collision_nodes:
        solids = collision.node().getSolids()
        if len(solids) > 0:
            first_solid = solids[0]
            if type(first_solid) is CollisionBox:
                shape = BulletBoxShape.makeFromSolid(first_solid)
            if type(first_solid) is CollisionPlane:
                shape = BulletPlaneShape.makeFromSolid(first_solid)
            if type(first_solid) is CollisionSphere:
                shape = BulletSphereShape.makeFromSolid(first_solid)
            if type(first_solid) is CollisionCapsule:
                shape = BulletCapsuleShape.makeFromSolid(first_solid)
            if type(first_solid) is CollisionPolygon:
                mesh = BulletTriangleMesh()
                for solid in solids:
                    p1 = solid.points[0]
                    p2 = solid.points[1]
                    p3 = solid.points[2]
                    mesh.addTriangle(p1, p2, p3)
                shape = BulletTriangleMeshShape(mesh, dynamic=False)

            panda_node = collision.parent
            ghost = panda_node.getTag("ghost")
            if ghost:
                panda_node.find("**/+GeomNode").remove_node()
                rigid_body_node = BulletGhostNode(collision.name)
                bullet_world.attachGhost(rigid_body_node)
            else:
                rigid_body_node = BulletRigidBodyNode(collision.name)
                bullet_world.attachRigidBody(rigid_body_node)
                
                friction = panda_node.getTag("friction")
                mass = panda_node.getTag("mass")
                bounce = panda_node.getTag("bounce")
            
                if friction:
                    rigid_body_node.setFriction(float(friction))
                if mass:
                    rigid_body_node.setFriction(float(mass))
                if bounce:
                    rigid_body_node.setRestitution(float(bounce))

            rigid_body_node.addShape(shape)
            np = panda_node.attach_new_node(rigid_body_node)
            np.setCollideMask(BitMask32.allOn())
            collision.remove_node()