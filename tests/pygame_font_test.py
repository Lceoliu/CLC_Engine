import pygame, sys

if __name__ == "__main__":
    pygame.init()
    fonts = pygame.font.get_fonts()
    fonts.sort()

    print("Available fonts:")
    for font in fonts:
        print(font)
        
    yahei = "microsoftyahei"
    yahei_ui = "microsoftyaheiui"
    fangsong = "fangsong"

    if yahei in fonts:
        print(f"Font '{yahei}' is available.")
    if yahei_ui in fonts:
        print(f"Font '{yahei_ui}' is available.")
    if fangsong in fonts:
        print(f"Font '{fangsong}' is available.")

    test_window = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Font Test")

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        test_window.fill((255, 255, 255))

        # Test rendering fonts
        font = pygame.font.SysFont(yahei, 36)
        text_surface = font.render("微软雅黑，。！？", True, (0, 0, 0))
        test_window.blit(text_surface, (50, 50))

        font = pygame.font.SysFont(yahei_ui, 36)
        text_surface = font.render("微软雅黑UI，。！？", True, (0, 0, 0))
        test_window.blit(text_surface, (50, 100))

        font = pygame.font.SysFont(fangsong, 36)
        text_surface = font.render("仿宋，。！？", True, (0, 0, 0))
        test_window.blit(text_surface, (50, 150))

        pygame.display.flip()
