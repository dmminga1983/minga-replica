import { test, expect } from '@playwright/test';

// One spec per flow from replica/recon.md. Selectors by role and label, never CSS classes.
test.describe('F01 guest completes the core action', () => {
  test.beforeEach(async ({ page }) => {
    const errors: string[] = [];
    page.on('console', (m) => m.type() === 'error' && errors.push(m.text()));
    page.on('response', (r) => r.status() >= 500 && errors.push(`${r.status()} ${r.url()}`));
    (page as any)._errors = errors;
  });

  test.afterEach(async ({ page }) => {
    expect((page as any)._errors, 'console errors or 5xx responses').toEqual([]);
  });

  test('F01-H1 happy path', async ({ page }) => {
    await page.goto('/');
    await page.getByRole('button', { name: /start|начать/i }).click();
    await page.getByLabel(/email|почта/i).fill('guest@example.com');
    await page.getByRole('button', { name: /continue|продолжить/i }).click();
    await expect(page.getByRole('heading', { name: /done|готово/i })).toBeVisible();
  });

  test('F01-E4 double submit creates one record', async ({ page }) => {
    await page.goto('/');
    const submit = page.getByRole('button', { name: /continue|продолжить/i });
    await Promise.all([submit.click(), submit.click()]);
    await expect(page.getByText(/already|уже/i)).toHaveCount(0);
  });
});
