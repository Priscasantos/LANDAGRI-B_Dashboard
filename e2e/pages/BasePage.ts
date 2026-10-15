import { Page } from '@playwright/test';
import { TIMEOUTS } from '../fixtures/testData';

export class BasePage {
  constructor(protected page: Page) {}

  async navigate(route: string) {
    await this.page.goto(route, { waitUntil: 'networkidle', timeout: TIMEOUTS.pageLoad });
    await this.waitForPageReady();
  }

  async waitForPageReady() {
    await this.page.waitForLoadState('networkidle', { timeout: TIMEOUTS.pageLoad });
    await this.page.waitForTimeout(TIMEOUTS.animation);
  }

  async waitForNavigationComplete() {
    await this.page.waitForTimeout(TIMEOUTS.transition);
    await this.page.waitForLoadState('networkidle', { timeout: TIMEOUTS.pageLoad });
  }

  async getPageTitle() {
    return this.page.title();
  }

  async isElementVisible(testId: string) {
    return this.page.getByTestId(testId).first().isVisible();
  }

  async takeScreenshot(name: string) {
    await this.page.screenshot({ path: `screenshots/${name}.png`, fullPage: true });
  }

  async getMetricValue(metricTestId: string) {
    const metric = this.page.getByTestId(metricTestId);
    return metric.textContent();
  }

  async getConsoleErrors(): Promise<string[]> {
    const errors: string[] = [];
    this.page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text());
    });
    return errors;
  }

  getEChartsCharts() {
    return this.page.locator('figure div svg');
  }

  async getEChartsChartCount() {
    return (await this.getEChartsCharts()).count();
  }

  async isMobileView() {
    const viewport = this.page.viewportSize();
    return viewport ? viewport.width < 768 : false;
  }
}
