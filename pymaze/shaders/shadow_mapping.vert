#version 330 core

layout(location = 0) in vec3 vPos;
layout(location = 3) in vec3 vInst;

uniform mat4 projView;

// Should do this on the code side rather than on shader
mat4 rotationMatrix(vec3 axis, float angle) {
    axis = normalize(axis);
    float s = sin(angle);
    float c = cos(angle);
    float oc = 1.0 - c;
    
    return mat4(oc * axis.x * axis.x + c,           oc * axis.x * axis.y - axis.z * s,  oc * axis.z * axis.x + axis.y * s,  0.0,
                oc * axis.x * axis.y + axis.z * s,  oc * axis.y * axis.y + c,           oc * axis.y * axis.z - axis.x * s,  0.0,
                oc * axis.z * axis.x - axis.y * s,  oc * axis.y * axis.z + axis.x * s,  oc * axis.z * axis.z + c,           0.0,
                0.0,                                0.0,                                0.0,                                1.0);
}

void main()
{
    vec3 inst = vInst;
	inst.y = 0.0f;

	mat4 model = mat4(1.0f);

	// Apply rotation
	bool dir = bool(int(vInst.y));
	if (dir){
		model = rotationMatrix(vec3(0.0f, 1.0f, 0.0f), radians(90.0f));
	}

	// Apply translation
	model[3][0] = inst.x;
	model[3][1] = inst.y;
	model[3][2] = inst.z;
    
    gl_Position = projView * model * vec4(vPos, 1.0f);
}