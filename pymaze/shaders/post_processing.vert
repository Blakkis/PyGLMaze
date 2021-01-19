#version 330 core

layout (location = 0) in vec2 aPos;
layout (location = 1) in vec2 aTexCoords;

out vec2 texCoords;

/*
vec2 rotate(vec2 v, float a) {
	float s = sin(a);
	float c = cos(a);
	mat2 m = mat2(c, -s, s, c);
	return m * v;
}

uniform float uSeconds;
*/

void main()
{
    //gl_Position = vec4(rotate(aPos.xy, radians(uSeconds * 8.0f)), 0.0f, 1.0f); 
    gl_Position = vec4(aPos.xy, 0.0f, 1.0f);
    texCoords = aTexCoords;
}  