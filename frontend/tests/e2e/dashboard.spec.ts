import { expect, test } from "@playwright/test";

test("loads live backend telemetry into the mission dashboard", async ({ page }) => {
  const consoleErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error") {
      consoleErrors.push(message.text());
    }
  });

  const apiResponse = page.waitForResponse(
    (response) => response.url().includes("/v1/reentries") && response.status() === 200,
  );

  await page.goto("/");
  await apiResponse;

  await expect(page.getByRole("img", { name: "WhereItFalls" })).toBeVisible();
  await expect(page.locator(".metric").filter({ hasText: "Objetos monitorados" })).toBeVisible();
  await expect(page.getByText("Risco global de reentrada")).toBeVisible();
  await expect(page.getByLabel("Mapa global navegável de risco de reentrada")).toBeVisible();
  await expect(page.locator(".leaflet-container")).toBeVisible();
  await expect(page.locator(".risk-map-marker").first()).toBeVisible();
  await page.getByRole("button", { name: "Salvar política" }).click();
  await expect(page.getByText(/ativo para DF/)).toBeVisible();
  await page.getByRole("button", { name: "Simular envio" }).click();
  await expect(page.getByText(/alerta\(s\) simulados/)).toBeVisible();
  expect(consoleErrors).toEqual([]);
});

test("keeps the operational layout usable on mobile", async ({ page }) => {
  await page.goto("/");

  await expect(page.getByRole("img", { name: "WhereItFalls" })).toBeVisible();
  await expect(page.getByText("Risco global de reentrada")).toBeVisible();
  await expect(page.getByLabel("Mapa global navegável de risco de reentrada")).toBeVisible();
  await expect(page.locator(".leaflet-container")).toBeVisible();
  const dimensions = await page.evaluate(() => ({
    viewport: window.innerHeight,
    body: document.documentElement.scrollHeight,
  }));
  expect(dimensions.body).toBeLessThanOrEqual(dimensions.viewport);
});
