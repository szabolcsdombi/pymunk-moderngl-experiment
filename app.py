import struct
import ModernGL
from PIL import Image

import pymunk
from pymunk import Vec2d


class App:
    def __init__(self):
        self.ctx = ModernGL.create_context()
        ctx = self.ctx

        self.prog = ctx.program([
            ctx.vertex_shader('''
                #version 330

                uniform vec4 Camera;

                // Per vertex
                in vec2 in_vert;
                in vec2 in_texture;

                // Per instance
                in vec3 in_pos;
                in vec2 in_size;
                in vec4 in_tint;

                out vec2 v_vert;
                out vec2 v_texture;
                out vec4 v_tint;

                void main() {
                    mat2 rotate = mat2(
                        cos(in_pos.z), sin(in_pos.z),
                        -sin(in_pos.z), cos(in_pos.z)
                    );
                    v_vert = rotate * (in_vert * in_size) + in_pos.xy;
                    gl_Position = vec4((v_vert - Camera.xy) / Camera.zw, 0.0, 1.0);
                    v_texture = in_texture;
                    v_tint = in_tint;
                }
            '''),
            ctx.fragment_shader('''
                #version 330

                uniform sampler2D Texture;

                in vec2 v_vert;
                in vec2 v_texture;
                in vec4 v_tint;

                out vec4 f_color;

                void main() {
                    vec4 tex = texture(Texture, v_texture);
                    vec3 color = tex.rgb * (1.0 - v_tint.a) + v_tint.rgb * v_tint.a;
                    f_color = vec4(color, tex.a);
            }
            '''),
        ])

        img = Image.open('data/crate.png').convert('RGBA')
        self.tex1 = ctx.texture(img.size, 4, img.tobytes())
        self.tex1.use(0)

        img = Image.open('data/ball.png').convert('RGBA')
        self.tex2 = ctx.texture(img.size, 4, img.tobytes())
        self.tex2.use(1)

        vbo1 = ctx.buffer(struct.pack('16f',
            -1.0, -1.0, 0.0, 0.0,
            -1.0, 1.0, 0.0, 1.0,
            1.0, -1.0, 1.0, 0.0,
            1.0, 1.0, 1.0, 1.0,
        ))

        self.vbo2 = ctx.buffer(reserve=1024*1024)

        vao_content = [
            (vbo1, '2f2f', ['in_vert', 'in_texture']),
            (self.vbo2, '3f2f4f/i', ['in_pos', 'in_size', 'in_tint']),
        ]

        self.vao = ctx.vertex_array(self.prog, vao_content)

        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)

        shape = pymunk.Segment(self.space.static_body, (5, 100), (595,100), 1.0)
        shape.friction = 1.0
        self.space.add(shape)

        x=Vec2d(-270, 7.5) + (300,100)
        y=Vec2d(0,0)
        deltaX=Vec2d(0.5625, 1.1)*20
        deltaY=Vec2d(1.125, 0.0)*20

        self.bodies = []
        self.balls = []

        for x in range(5):
            for y in range(10):
                size = 20
                mass = 10.0
                moment = pymunk.moment_for_box(mass, (size, size))
                body = pymunk.Body(mass, moment)
                body.position = Vec2d(300 + x*50, 105 + y * (size +.1))
                shape = pymunk.Poly.create_box(body, (size, size))
                shape.friction = 0.3
                self.space.add(body,shape)
                self.bodies.append(body)
    
    def shoot(self):
        mass = 100
        r = 15
        moment = pymunk.moment_for_circle(mass, 0, r, (0,0))
        body = pymunk.Body(mass, moment)
        body.position = (0, 165)
        shape = pymunk.Circle(body, r, (0,0))
        shape.friction = 0.3
        self.space.add(body, shape)
        f = 50000
        body.apply_impulse_at_local_point((f,0), (0,0))
        self.balls.append(body)

    def render(self, viewport, elapsed):
        ctx = self.ctx
        ctx.viewport = viewport
        ctx.clear(240, 240, 240)
        ctx.enable(ModernGL.BLEND)

        for i in range(10):
            self.space.step(0.001)

        self.prog.uniforms['Camera'].value = (200, 300, viewport[2] / 2, viewport[3] / 2)

        self.vbo2.write(b''.join(struct.pack('3f2f4f', b.position.x, b.position.y, b.angle, 10, 10, 1, 1, 1, 0) for b in self.bodies))
        self.prog.uniforms['Texture'].value = 0
        self.vao.render(ModernGL.TRIANGLE_STRIP, instances=len(self.bodies))

        self.vbo2.orphan()

        self.vbo2.write(b''.join(struct.pack('3f2f4f', b.position.x, b.position.y, b.angle, 15, 15, 1, 1, 1, 0) for b in self.balls))
        self.prog.uniforms['Texture'].value = 1
        self.vao.render(ModernGL.TRIANGLE_STRIP, instances=len(self.balls))
