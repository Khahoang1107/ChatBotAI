
# ChatBotAI Frontend

Modern React + TypeScript frontend for ChatBotAI application with beautiful UI components.

## 🚀 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Radix UI** - Headless UI components
- **Lucide React** - Icons
- **React Hook Form** - Form management
- **Sonner** - Toast notifications

## 📁 Project Structure

```
frontend/
├── src/
│   ├── assets/          # Static assets (images, icons)
│   ├── components/      # Reusable UI components
│   │   └── ui/         # shadcn/ui components
│   ├── constants/       # Configuration and constants
│   ├── hooks/          # Custom React hooks
│   ├── pages/          # Page components
│   ├── services/       # API and business logic services
│   ├── styles/         # Global styles
│   ├── types/          # TypeScript type definitions
│   ├── utils/          # Utility functions
│   ├── App.tsx         # Main app component
│   ├── main.tsx        # Entry point
│   └── index.css       # Global CSS
├── public/             # Public static files
├── .env.example        # Environment variables example
├── index.html          # HTML entry point
├── package.json        # Dependencies
├── tsconfig.json       # TypeScript config
├── vite.config.ts      # Vite config
└── tailwind.config.js  # Tailwind config
```

## 🛠️ Setup & Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Setup environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` file with your configuration.

3. **Run development server:**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:3000`

## 📜 Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 🔐 Mock Accounts

For development and testing:

**Admin Account:**
- Email: `admin@invoice.com`
- Password: `admin123`

**User Account:**
- Email: `user@invoice.com`
- Password: `user123`

## 🎨 Features

- ✅ Login & Registration
- ✅ User Dashboard
- ✅ Admin Dashboard
- ✅ Profile Settings
- ✅ Responsive Design
- ✅ Dark Mode Support
- ✅ Form Validation
- ✅ Toast Notifications

## 🔧 Development Guidelines

### Adding New Components

1. Create component in `src/components/` or `src/pages/`
2. Use TypeScript for type safety
3. Follow naming conventions (PascalCase for components)
4. Export from index file if needed

### Adding New Services

1. Create service file in `src/services/`
2. Use class-based approach for organization
3. Add proper TypeScript types
4. Document with JSDoc comments

### Adding New Hooks

1. Create hook file in `src/hooks/`
2. Prefix with `use` (e.g., `useAuth`, `useForm`)
3. Add proper TypeScript types
4. Export from hook file

## 🌐 API Integration

The frontend is configured to proxy API requests to the backend:

- Development: `http://localhost:8000`
- API endpoints: `/api/*`

Configure in `vite.config.ts` if backend URL changes.

## 📦 Building for Production

```bash
npm run build
```

This will create an optimized production build in the `dist/` directory.

## 🤝 Contributing

1. Follow the existing code style
2. Use TypeScript strictly
3. Add types for all props and functions
4. Test your changes before committing
5. Keep components small and focused

## 📄 License

Private - ChatBotAI Project
  