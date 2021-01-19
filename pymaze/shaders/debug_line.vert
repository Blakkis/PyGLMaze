#version 330 core

layout(location = 0) in vec3 vPos;

uniform mat4 projView;

void main()
{
    gl_Position = projView * vec4(vPos, 1.0f);
}