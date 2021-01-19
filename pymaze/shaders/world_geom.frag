#version 330 core

out vec4 fragColor;

in vec2 aTexCoords;
in vec3 aNormal;
in vec4 aFragPosLight;

uniform sampler2D diffuse;
uniform sampler2D shadowMap;

uniform vec2 textureScale;
uniform vec3 lightDir;


float getShadowFragmentSun(vec4 fragPosLight)
{
    vec3 projCoords = (fragPosLight.xyz / fragPosLight.w) * 0.5f + 0.5f;
    
    float shadow = 0.0f;    // Shadow accumulator

    vec2 texelSize = 1.0f / textureSize(shadowMap, 0);
    for(int x = -1; x <= 1; x++)
    {
        for(int y = -1; y <= 1; y++)
        {
            float depthValue = texture(shadowMap, projCoords.xy + vec2(x, y) * texelSize).r; 
            shadow += projCoords.z > depthValue ? 1.0f : 0.0f;        
        }    
    }
    
    return (projCoords.z > 1.0) ? 0.0f : shadow / 9.0f; 
}


void main()
{
	vec3 color = texture(diffuse, aTexCoords * textureScale).rgb;
	float shadow = 1.0f;

	// All fragments that are facing away from the sun can be covered in shadow fully (duh)
	if (dot(aNormal, lightDir) < 0.0f){
		shadow = getShadowFragmentSun(aFragPosLight);
	}

	vec3 finalOut = (color + (1.0f - shadow)) * color;
    fragColor = vec4(finalOut, 1.0f);
}