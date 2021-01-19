#version 330 core

layout (location = 0) in vec3 aPos;

out vec3 TexCoords;

uniform mat4 projView;

void main()
{
    TexCoords = aPos * -1.0f;	// Quick fix to flip the texture 180
    vec4 pos = projView * vec4(aPos, 1.0f);
    gl_Position = pos.xyww;
}  