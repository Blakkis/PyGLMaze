#version 330 core

layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aTexCoords;

out vec2 texCoords;

uniform vec2 uResolution;

uniform mat4 projView;
uniform mat4 model;

void main()
{
	float aspect = uResolution.x / uResolution.y;
    gl_Position = projView * model * vec4(aPos.xy * vec2(aspect, 1.0f), 0.0f, 1.0f);
    texCoords = aTexCoords;
}  