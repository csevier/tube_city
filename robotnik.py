from panda3d.core import (CollisionBox, 
                         CollisionSphere,
                         CollisionCapsule, 
                         CollisionPlane,
                         CollisionPolygon
                         )
from panda3d.bullet import (BulletPlaneShape, 
                            BulletBoxShape, 
                            BulletRigidBodyNode, 
                            BulletSphereShape,
                            BulletCapsuleShape,
                            BulletTriangleMeshShape,
                            BulletHeightfieldShape,
                            BulletTriangleMesh)

def collision_to_rigidbody(bullet_world, node_path):
    collision_nodes = node_path.findAllMatches("**/+CollisionNode")
    for collision in collision_nodes:
        solids = collision.node().getSolids()
        panda_node = collision.parent
        if len(solids) > 1:
            first_solid = solids[0]
            if type(first_solid) is CollisionBox:
                shape = BulletBoxShape.makeFromSolid(solid)
            if type(first_solid) is CollisionPlane:
                shape = BulletPlaneShape.makeFromSolid(solid)
            if type(first_solid) is CollisionSphere:
                shape = BulletSphereShape.makeFromSolid(solid)
            if type(first_solid) is CollisionCapsule:
                shape = BulletCapsuleShape.makeFromSolid(solid)
            if type(first_solid) is CollisionPolygon:
                mesh = BulletTriangleMesh()
                for solid in solids:
                    pass
                   # mesh.addTriangle(p0, p1, p2)
                   # mesh.addTriangle(p1, p2, p3)
                shape = BulletTriangleMeshShape(mesh, dynamic=False)
            else:
                continue
        
            rigid_body_node = BulletRigidBodyNode(collision.name)
            rigid_body_node.addShape(shape)
            panda_node.attach_new_node(rigid_body_node)
            bullet_world.attachRigidBody(rigid_body_node)
            collision.remove()
            panda_node.ls()