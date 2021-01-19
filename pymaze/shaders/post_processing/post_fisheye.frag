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

    float aperture = 180.0f;
    float apertureHalf = 0.5f * aperture * (PI / 180.0f);
    float maxFactor = sin(apertureHalf);

    vec2 uv;
    vec2 xy = 2.0f * texCoords.xy - 1.0f;
    xy.x *= uResolution.x / uResolution.y;

    float d = length(xy);
    float rad = 2.0f - maxFactor;

    float s = 0.5f * (0.5f + sin(uSeconds) * 0.5f);

    if (d > (rad - 0.5) && d < rad)
    {
        d = length(xy * maxFactor);
        float z = sqrt(1.0f - d * d);
        float r = atan(d, z) / PI;
        float phi = atan(xy.y, xy.x);
        
        uv.x = r * cos(phi) + 0.5f + smoothstep(0.5f - s, 0.5f + s, d);
        uv.y = r * sin(phi) + 0.5f + smoothstep(0.5f - s, 0.5f + s, d);
    }
    else
    {
        uv = texCoords.xy;
    }

    vec4 c = texture2D(colorTexture, uv);
    fragColor = c;
} 