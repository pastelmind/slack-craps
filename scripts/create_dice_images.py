"""Creates images of all possible rolls of two dice, using images of a die."""
from os import path

from PIL import Image


def create_dice_images(image_dir: str) -> None:
    """Creates images of all possible rolls of two dice."""
    image_names = [path.join(image_dir, f"die-{i}.png") for i in range(1, 7)]
    images = [Image.open(name) for name in image_names]
    images = [image.convert() for image in images]

    for i, image in enumerate(images):
        if i == 0:
            continue
        assert image.size == images[0].size, (
            f"{image_names[i]}: incorrect size "
            f"(expected {images[0].size}, got {image.size})"
        )

    mode = images[0].mode
    width, height = images[0].size

    for a, image_a in enumerate(images):
        die_a = image_a.crop()
        for b, image_b in enumerate(images):
            die_b = image_b.crop()

            dice_image = Image.new(mode=mode, size=(width * 2, height))
            dice_image.paste(die_a)
            dice_image.paste(die_b, box=(width, 0))

            dice_image.save(path.join(image_dir, f"dice-{a + 1}-{b + 1}.png"))


if __name__ == "__main__":
    create_dice_images("./images")
