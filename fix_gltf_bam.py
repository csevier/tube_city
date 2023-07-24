from panda3d.core import MaterialAttrib, Vec4, TextureAttrib, RenderState, TextureStage

def render_stage_convert(node, use_modulate = False, use_normal = False, use_selector = False, use_emission = False):
    for node_path in node.find_all_matches('**/+GeomNode'):
        geom_node = node_path.node()
        new_render_state = RenderState.make_empty()
        for index_geom in range(geom_node.get_num_geoms()):
            render_state = geom_node.get_geom_state(index_geom)
            if render_state.has_attrib(MaterialAttrib):
                material = render_state.get_attrib(MaterialAttrib).get_material()
                #material.set_diffuse(Vec4(*material.get_base_color()))
                material.set_twoside(False)
                material.set_refractive_index(1)
                material.set_shininess(0)
                material.clear_metallic()
                #material.clear_diffuse()
                #material.clear_base_color()
                material.clear_ambient()
                material.clear_emission()
                new_render_state = new_render_state.add_attrib(MaterialAttrib.make(material))
            if render_state.has_attrib(TextureAttrib):
                new_texture_attrib = TextureAttrib.make_default()
                texture_attrib = render_state.get_attrib(TextureAttrib)
                count_stages = texture_attrib.get_num_on_stages()
                for index_texture_stage in range(count_stages):
                    texture_stage = texture_attrib.get_on_stage(index_texture_stage)
                    texture = render_state.get_attrib(TextureAttrib).get_on_texture(texture_stage)
                    sampler = render_state.get_attrib(TextureAttrib).get_on_sampler(texture_stage)
                    if texture_stage.get_mode() == TextureStage.M_modulate:
                        if use_modulate:
                            new_texture_attrib = new_texture_attrib.add_on_stage(texture_stage, texture, sampler)
                    if texture_stage.get_mode() == TextureStage.M_normal:
                        if use_normal:
                            new_texture_attrib = new_texture_attrib.add_on_stage(texture_stage, texture, sampler)
                    if texture_stage.get_mode() == TextureStage.M_selector:
                        if use_selector:
                            new_texture_attrib = new_texture_attrib.add_on_stage(texture_stage, texture, sampler)
                    if texture_stage.get_mode() == TextureStage.M_emission:
                        if use_emission:
                            new_texture_attrib = new_texture_attrib.add_on_stage(texture_stage, texture, sampler)
                if new_texture_attrib.get_num_on_stages() > 0:
                    new_render_state = new_render_state.add_attrib(new_texture_attrib)
                geom_node.set_geom_state(index_geom, new_render_state)