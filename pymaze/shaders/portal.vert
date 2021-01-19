#version 330 core

layout(location = 0) in vec3 aPos;
layout(location = 1) in vec2 aTexCoords;

out vec2 texCoords;

uniform mat4 projView;
uniform mat4 view;
uniform mat4 model;

void main()
{
	mat4 view_inv = inverse(view);
	vec3 center = model[3].xyz;
	
	vec3 cam_right = view_inv[0].xyz;
	vec3 cam_up = view_inv[1].xyz;

	vec3 pos = center + (cam_right * aPos.x) + (cam_up * aPos.y);
    gl_Position = projView * model * vec4(pos, 1.0f);

    texCoords = aTexCoords;
}