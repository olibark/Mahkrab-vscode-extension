#include <SDL2/SDL.h>
#include <SDL2/SDL_image.h>
#include <SDL2/SDL_ttf.h>
#include <stdio.h> 
#include <stdlib.h>
#include <time.h>

#define WINDOW_WIDTH  600
#define WINDOW_HEIGHT 600
#define NUM_PARTICLES 2000

typedef struct {
    float x, y;      // Current positio
    float vx, vy;    // Velocity
    int size;
    SDL_Color color;
} Particle;

int main(int argc, char *argv[]) {
    // Seed random number generator
    srand((unsigned int)time(NULL));

    // Initialize SDL
    if (SDL_Init(SDL_INIT_VIDEO) < 0) {
        SDL_Log("Failed to initialize SDL: %s", SDL_GetError());
        return 1;
    }

    // Create an SDL window
    SDL_Window *window = SDL_CreateWindow(
        "Bouncing Particles",
        SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
        WINDOW_WIDTH, WINDOW_HEIGHT,
        SDL_WINDOW_SHOWN
    );
    if (!window) {
        SDL_Log("Failed to create window: %s", SDL_GetError());
        SDL_Quit();
        return 1;
    }

    // Create a renderer for the window
    SDL_Renderer *renderer = SDL_CreateRenderer(
        window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_PRESENTVSYNC
    );
    if (!renderer) {
        SDL_Log("Failed to create renderer: %s", SDL_GetError());
        SDL_DestroyWindow(window);
        SDL_Quit();
        return 1;
    }

    // Create and initialize particles
    Particle particles[NUM_PARTICLES];
    for (int i = 0; i < NUM_PARTICLES; i++) {
        particles[i].x = (float)(rand() % WINDOW_WIDTH);
        particles[i].y = (float)(rand() % WINDOW_HEIGHT);
        // Random velocity between -5 and 5
        particles[i].vx = (float)((rand() % 101) / 10.0f - 5.0f);
        particles[i].vy = (float)((rand() % 101) / 10.0f - 5.0f);
        particles[i].size = rand() % 5 + 5; // Radius between 5 and 9
        // Give each particle a random colour
        particles[i].color.r = rand() % 256;
        particles[i].color.g = rand() % 256;
        particles[i].color.b = rand() % 256;
        particles[i].color.a = 255;
    }

    // Main loop flag
    int running = 1;
    // Frame rate limiter (optional)
    const int frameDelay = 16; // ~60 FPS
    Uint32 frameStart;
    int frameTime;

    while (running) {
        frameStart = SDL_GetTicks();

        // Event handling
        SDL_Event event;
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT) {
                running = 0;
            }
            if (event.type == SDL_KEYDOWN) {
                if (event.key.keysym.sym == SDLK_ESCAPE) {
                    running = 0;
                }
            }
        }

        // Update particle positions
        for (int i = 0; i < NUM_PARTICLES; i++) {
            // Move particle
            particles[i].x += particles[i].vx;
            particles[i].y += particles[i].vy;

            // Check collision with window boundaries
            if (particles[i].x < 0) {
                particles[i].x = 0;
                particles[i].vx = -particles[i].vx;
            } else if (particles[i].x > WINDOW_WIDTH - particles[i].size) {
                particles[i].x = WINDOW_WIDTH - particles[i].size;
                particles[i].vx = -particles[i].vx;
            }
            if (particles[i].y < 0) {
                particles[i].y = 0;
                particles[i].vy = -particles[i].vy;
            } else if (particles[i].y > WINDOW_HEIGHT - particles[i].size) {
                particles[i].y = WINDOW_HEIGHT - particles[i].size;
                particles[i].vy = -particles[i].vy;
            }
        }

        // Clear the screen
        SDL_SetRenderDrawColor(renderer, 0, 0, 0, 255);
        SDL_RenderClear(renderer);

        // Render each particle
        for (int i = 0; i < NUM_PARTICLES; i++) {
            SDL_SetRenderDrawColor(renderer,
                                   particles[i].color.r,
                                   particles[i].color.g,
                                   particles[i].color.b,
                                   255);
            // Draw a small filled square for simplicity (or you can draw circles)
            SDL_Rect rect = {
                (int)particles[i].x,
                (int)particles[i].y,
                particles[i].size,
                particles[i].size
            };
            SDL_RenderFillRect(renderer, &rect);
        }

        // Present the updated frame
        SDL_RenderPresent(renderer);

        // Simple frame rate control (optional)
        frameTime = SDL_GetTicks() - frameStart;
        if (frameDelay > frameTime) {
            SDL_Delay(frameDelay - frameTime);
        }
    }

    // Cleanup
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();

    return 0;
}
