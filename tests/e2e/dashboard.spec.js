const { test, expect } = require("@playwright/test");

test("dashboard renders, filters, pivots, and creates an order", async ({ page }) => {
  const orderNo = `ORD-E2E-${Date.now()}`;

  await page.goto("/");

  await expect(page.getByRole("heading", { name: "销售数据透视分析面板" })).toBeVisible();
  await expect(page.getByText("总订单数")).toBeVisible();
  await expect(page.getByText("36")).toBeVisible();

  await page.getByTestId("city-filter").click();
  await page.getByRole("option", { name: "北京" }).click();
  await page.keyboard.press("Escape");
  await page.getByTestId("search-button").click();

  await expect(page.locator(".summary-card")).toContainText(["总订单数"]);
  await expect(page.getByTestId("pivot-table")).toBeVisible();

  await page.getByTestId("metric-select").click();
  await page.getByRole("option", { name: "平均客单价" }).click();
  await expect(
    page.getByText("平均客单价 = 当前分组内 amount 总和 / 当前分组订单数")
  ).toBeVisible();

  await page.getByRole("button", { name: "新增订单" }).click();
  await page.getByTestId("order-no-input").locator("input").fill(orderNo);
  await page.getByTestId("created-at-input").locator("input").fill("2025-06-15 10:10:10");
  await page.getByTestId("amount-input").locator("input").fill("1888");
  await page.getByTestId("submit-order").click();

  await expect(page.getByText("订单新增成功")).toBeVisible();
});
