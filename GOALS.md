# Goals & Objectives — Django Blog Project

## Overview

A multi-author blog platform built with Django, designed to be showcased as a demo to clients and buyers. The platform allows any registered user to write, manage, and publish blog posts, while visitors can freely browse and read content without an account.

---

## Business Goals

1. **Demonstrate a production-quality Django web application** suitable for client presentation and staging deployment.
2. **Provide a fully functional multi-author blog** where users can independently manage their own content.
3. **Deliver a polished, device-friendly UI** that works seamlessly on desktop, tablet, and mobile.
4. **Give readers tools to track and manage their reading** so the platform feels more like a product than a demo.
5. **Allow non-technical owners to control key site content** (name, branding, about page) without touching code.
6. **Establish a maintainable, extensible codebase** that can be handed off or built upon after the demo.

---

## Objectives

### User Experience
- Visitors can browse, read, search, and filter posts without creating an account
- Registered users can create, edit, and delete their own posts from the frontend (no admin panel required)
- Authors write posts using a rich text editor with formatting support (bold, headings, images, lists, tables)
- Posts are organised by categories and tags for easy discovery
- All pages are fully responsive and usable on all screen sizes
- Users can switch between dark and light themes; preference persists across sessions
- Users can set their preferred reading font size (Small / Medium / Large); preference persists across sessions

### Reading & Engagement
- Authenticated users can mark any post as Read — status persists after logout and re-login
- Authenticated users can save posts for later and access them from a dedicated Reading List page
- Reading List supports tabs (Saved / Read History) and filters (category, tag, read status)
- Homepage offers quick filters: All Posts / Unread / Read / Saved
- Each post card shows read and saved status badges at a glance
- Estimated reading time is shown on each post card

### Content Management
- Each post has a title, rich content body, optional cover image, category, tags, and a draft/published status
- Authors can save posts as drafts before publishing
- Posts use SEO-friendly slugs in their URLs

### User Management
- Users can register, log in, and log out
- Users who forget their password can reset it via an email link
- Each user has a profile page showing their avatar, join date, post count, read count, and saved count
- Users can update their username, email, and profile picture from their profile page

### Discovery & Navigation
- Site-wide search by post title and content
- Filter posts by category or tag
- Sidebar shows categories, recent posts, and a search box on all listing pages
- Paginated post listings — posts-per-page is configurable via Site Settings
- Navbar shows a live saved-posts badge that updates without page reload

### Site Administration
- A singleton Site Settings model lets the admin update site name, browser tab title, hero heading, hero subtext, about page content (rich text), and posts per page — all without touching code
- Full Django admin panel for managing posts, categories, tags, users, read records, and saved records

### Technical
- PostgreSQL database with environment-variable-based configuration
- Secure handling of secrets via `.env` file (never committed to version control)
- Email backend switchable via environment: console output in development, SMTP in production
- Static and media files properly configured
- Context processors inject global data (saved count, site settings) without repeating logic in every view
- Codebase ready for staging deployment

---

## Success Criteria

- All features work end-to-end without errors
- UI passes a basic review on mobile (375px), tablet (768px), and desktop (1280px)
- A client/buyer can register, write a post, and view it live within 2 minutes of landing on the site
- A returning user can find unread or saved posts in one click from the homepage
- The site owner can rebrand the site (name, about page) entirely from the admin panel without touching code
- Password reset flow works in development (console) and is ready for production SMTP with only `.env` changes
- The staging environment is accessible via a public URL
