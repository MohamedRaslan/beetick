import { expect, type Locator } from "@playwright/test";

const IMAGE_TIMEOUT_MS = 10_000;

/** Product photography is 1080px square; anything small is a placeholder pixel. */
const MIN_INTRINSIC_WIDTH_PX = 200;

/** Product photography is served from the media CDN; fallback art is not. */
const PRODUCT_MEDIA_URL = /^https:\/\/media\.btech\.com\/catalogs\//;

type ImageState = {
  src: string;
  complete: boolean;
  naturalWidth: number;
};

async function imageState(image: Locator): Promise<ImageState> {
  return image.evaluate((element) => {
    const htmlImage = element as HTMLImageElement;

    return {
      src: htmlImage.currentSrc || htmlImage.src,
      complete: htmlImage.complete,
      naturalWidth: htmlImage.naturalWidth,
    };
  });
}

export async function expectProductImagePresent(
  image: Locator,
  productName: string,
): Promise<void> {
  await expect(image).toBeVisible();
  await expect(image).toHaveAttribute("alt", productName);
  await expect(image).toHaveAttribute("src", /\S/);
}

/**
 * Asserts the browser fetched and decoded the product's image. Proves the
 * resource loaded, not that it looks correct — see the image assertion section
 * of the root README.
 */
export async function expectLoadedImage(
  image: Locator,
  productName: string,
): Promise<void> {
  await image.scrollIntoViewIfNeeded();
  await expectProductImagePresent(image, productName);
  await expect(async () => {
    const state = await imageState(image);
    expect(state.src).toMatch(PRODUCT_MEDIA_URL);
    expect(state.complete).toBe(true);
    expect(state.naturalWidth).toBeGreaterThanOrEqual(MIN_INTRINSIC_WIDTH_PX);
  }).toPass({ timeout: IMAGE_TIMEOUT_MS });
}
