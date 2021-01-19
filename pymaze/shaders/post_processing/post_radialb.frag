#version 330 core

const float PI = 3.1415926535f;

out vec4 fragColor;

in vec2 texCoords;

uniform sampler2D colorTexture;
uniform sampler2D depthTexture; 

uniform float uSeconds;
uniform vec2 uResolution;

/*
    Inbuilt -
        "gl_FragCoord" = Pixel coordinate(vec2) between (0 - uResolution) from bottomleft
    
    
    Uniforms - 
        "uResolution" = Display resolution
        "uSeconds" = Game running time
*/


// Get depth (Linearized)
float getDepth(vec2 uv)
{
    // TODO: Bring these via uniforms?
    // Right now they need to match with the values in the "c_near" and "c_far" constants in "constants.py"
    float near = 0.01f;
    float far = 100.0f;

    // Linearize the depth
    float depth = texture2D(depthTexture, uv).x;
    return (2.0f * near) / (far + near - depth * (far - near));
}


// Get color
vec3 getColor(vec2 uv)
{
    return texture2D(colorTexture, uv).rgb;
}


#define T texture2D(colorTexture, 0.5f + (p.xy *= 0.992f))

void main()
{
    vec2 tex = texCoords;

    float depth = getDepth(tex);
    vec3 color = getColor(tex);

    // --------

    vec3 p = vec3(gl_FragCoord.xy / uResolution - 0.5f, 0.0f);
    vec3 o = T.rbb;
    for (float i = 0.0f; i < 100.0f; i++){
        p.z += pow(max(0.0f, 0.5f - length(T.rg)), 2.0f) * exp(-i * 0.008f);
    }

    fragColor = vec4(o * o + p.z, 1.0f);
} 