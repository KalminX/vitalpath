# VitalPath Education — Creator & Administrator Guide

Welcome to your **VitalPath Education** management dashboard!

This guide is written in plain, non-technical English to help you manage your digital products, monitor orders, keep track of students, and update your YouTube video lessons.

---

## 1. Logging In to Your Studio

1. Visit your website and click **Sign In** in the top navigation bar (or navigate directly to `/dashboard/login/`).
2. Enter your creator credentials:
   - **Email / Username**: `creator@vitalpath.edu`
   - **Password**: `VitalPath2026!`
3. Click **Sign In to Dashboard**. You will arrive at your **Creator Overview**.

---

## 2. Adding a New Product or Guide

To launch a new digital guide or curriculum:

1. Click **Products & Courses** in the left sidebar.
2. Click the **+ New Product** button in the top-right corner.
3. Fill in the straightforward product details:
   - **Product Title**: e.g., *"Sleep & Circadian Physiology Guide"*
   - **Price**: e.g., `24.00`
   - **Publishing Status**: Choose **Published** to make it live immediately, or **Draft** if you are still working on it.
   - **Short Description**: A 1–2 sentence summary displayed on the course card.
   - **Full Description**: Detailed explanation of what the course covers.
   - **What's Included**: List your deliverables, one per line (e.g., `8 video modules`, `45-page companion PDF`, `Daily checklist`).
   - **Who It's For**: List your target audience, one point per line.
   - **Target Outcomes**: What the learner will achieve.
4. Click **Save Product**. Your product page is automatically created and ready to accept payments!

---

## 3. Editing an Existing Product

1. Navigate to **Products & Courses**.
2. Find the product you wish to change and click the **Edit** button.
3. Update any fields (such as changing the price, updating description copy, or adding new deliverables).
4. Click **Save Product**. The public website will reflect your updates instantly.

---

## 4. Publishing & Unpublishing Products

You can quickly hide or publish any guide without deleting it:

- From the **Products & Courses** list, simply click the **Unpublish** or **Publish** button next to the product.
- **Draft** items are completely hidden from public visitors and search filters, but remain safely stored in your dashboard so you can edit them anytime.

---

## 5. Viewing and Managing Customers

Click **Customers** in the left sidebar to see everyone who has purchased from you.

- **Customer List**: Shows student names, emails, total purchases, and lifetime value ($ spent).
- **VIP Status**: The system automatically labels repeat buyers as **VIP** so you can give them special attention.
- **Customer Notes**: Click into any customer profile to view their full order history and record private notes (e.g., *"Student requested advanced nutrition module"*).

---

## 6. Viewing Orders & Receipts

Click **Orders & Payments** in the sidebar to review all transactions.

- **Order Search**: You can search by Order ID (e.g., `VP-78219`), student name, or email.
- **Order Details**: Click any order number to see:
  - Date and exact time of purchase.
  - Which guide was purchased.
  - The Stripe payment reference ID.
  - Confirmation email delivery status.

---

## 7. Understanding Payments & Stripe

Your platform uses **Stripe Checkout** for payment processing.

- When a customer purchases a product, Stripe processes their payment securely in the background.
- Once the payment succeeds, Stripe notifies your website, which automatically creates the order, registers the student, and sends them an email with access instructions.
- All funds go directly into your connected Stripe account and are paid out to your bank according to your Stripe payout schedule.

---

## 8. Updating YouTube Content & Free Resources

You can feature your latest YouTube videos directly on the homepage and resource hub without touching any code:

1. Click **YouTube Content** in the left sidebar.
2. Click **+ Add Video**.
3. Enter:
   - **Video Title**
   - **YouTube Video ID** (e.g., if your video link is `youtube.com/watch?v=y9x72V8cM7Q`, the ID is `y9x72V8cM7Q`)
   - **Duration**: e.g., `12:45`
   - **Category**: e.g., `Nutrition Principles`
   - Check **Feature on Homepage** if you want it displayed on the front page.
4. Click **Save Video**. It will now appear on your homepage and `/resources/` library!

---

## 9. What Future Telegram Integration Will Do

In upcoming phases, you will be able to:
1. **Send Announcements**: Draft a message in your dashboard and broadcast it directly to your public Telegram channel with one click.
2. **Private Membership Access**: When a customer subscribes to a future paid membership, the system will automatically generate a private single-use Telegram invite link and remove members if their subscription ends.
3. **Waitlist Review**: You can view all interested students who joined your waitlist by clicking **Membership Leads** in the dashboard.

---

## 10. Basic Troubleshooting

| Issue | What to check |
|---|---|
| **Cannot log in to dashboard** | Ensure you are visiting `/dashboard/login/` and using `creator@vitalpath.edu` with password `VitalPath2026!`. |
| **Product not showing on website** | Check that the product status is set to **Published** and not **Draft**. |
| **Customer says they didn't receive receipt email** | Check the order detail in your dashboard. If needed, click their email to send them a direct copy. |
| **Need to change site name or email address** | Open your `.env` settings file or update your site settings with your developer. |
