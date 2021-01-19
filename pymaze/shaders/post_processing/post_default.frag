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


void main()
{
    vec2 tex = texCoords;

    float depth = getDepth(tex);
    vec3 color = getColor(tex);

    // --------

    fragColor = vec4(color, 1.0f);
} 