# Frontend Development Guide

## 📂 Cấu trúc thư mục

### `src/assets/`
Chứa các tài nguyên tĩnh như hình ảnh, icons, fonts.

### `src/components/`
Chứa các React components có thể tái sử dụng:
- `ui/` - Shadcn/ui components (button, input, dialog, etc.)
- `figma/` - Components từ Figma design

### `src/constants/`
Chứa các hằng số và cấu hình:
- `config.ts` - Cấu hình app, API, routes
- `mockData.ts` - Dữ liệu mock cho development

### `src/hooks/`
Custom React hooks:
- `useAuth.ts` - Authentication logic
- Thêm hooks mới khi cần (useForm, useFetch, etc.)

### `src/pages/`
Các page components chính:
- `LoginPage.tsx` - Trang đăng nhập
- `SignupPage.tsx` - Trang đăng ký
- `UserDashboard.tsx` - Dashboard người dùng
- `AdminDashboard.tsx` - Dashboard admin
- `ProfileSettings.tsx` - Cài đặt profile

### `src/services/`
Business logic và API calls:
- `authService.ts` - Authentication service
- Thêm services mới khi cần (apiService, chatService, etc.)

### `src/styles/`
Global styles:
- `globals.css` - CSS toàn cục

### `src/types/`
TypeScript type definitions:
- `index.ts` - Tất cả types của app

### `src/utils/`
Utility functions:
- `helpers.ts` - Helper functions
- `validators.ts` - Form validation functions

## 🎯 Quy tắc Code

### Naming Conventions
- **Components**: PascalCase (`LoginPage.tsx`, `Button.tsx`)
- **Files**: camelCase (`authService.ts`, `useAuth.ts`)
- **Variables/Functions**: camelCase (`isAuthenticated`, `handleLogin`)
- **Constants**: UPPER_SNAKE_CASE (`API_BASE_URL`, `MOCK_ACCOUNTS`)
- **Types/Interfaces**: PascalCase (`User`, `LoginCredentials`)

### Component Structure
```tsx
// 1. Imports
import { useState } from 'react';
import { Button } from '@/components/ui/button';
import type { User } from '@/types';

// 2. Types/Interfaces
interface ComponentProps {
  user: User;
  onAction: () => void;
}

// 3. Component
export function Component({ user, onAction }: ComponentProps) {
  // 3.1. Hooks
  const [state, setState] = useState<string>('');

  // 3.2. Handlers
  const handleClick = () => {
    // logic
  };

  // 3.3. Effects
  useEffect(() => {
    // logic
  }, []);

  // 3.4. Render
  return (
    <div>
      {/* JSX */}
    </div>
  );
}
```

### TypeScript Best Practices
- Luôn định nghĩa types cho props
- Sử dụng interfaces cho object types
- Sử dụng type aliases cho unions/primitives
- Tránh sử dụng `any`, dùng `unknown` nếu cần

### Import/Export
```tsx
// ✅ Good - Named exports
export function MyComponent() {}
export const myFunction = () => {};

// ✅ Good - Using path aliases
import { Button } from '@/components/ui/button';
import { User } from '@/types';

// ❌ Bad - Default exports (trừ App.tsx)
export default function MyComponent() {}
```

## 🔧 Development Workflow

### 1. Thêm Page Mới
```bash
# 1. Tạo file trong src/pages/
touch src/pages/NewPage.tsx

# 2. Export trong src/pages/index.ts
export { NewPage } from './NewPage';

# 3. Sử dụng trong App.tsx
import { NewPage } from './pages';
```

### 2. Thêm Service Mới
```bash
# 1. Tạo file trong src/services/
touch src/services/newService.ts

# 2. Export trong src/services/index.ts
export { NewService } from './newService';

# 3. Sử dụng
import { NewService } from '@/services';
```

### 3. Thêm Custom Hook
```bash
# 1. Tạo file trong src/hooks/
touch src/hooks/useNewHook.ts

# 2. Export trong src/hooks/index.ts
export { useNewHook } from './useNewHook';

# 3. Sử dụng
import { useNewHook } from '@/hooks';
```

## 🎨 Styling Guidelines

### Tailwind Classes Order
1. Layout (display, position)
2. Flexbox/Grid
3. Spacing (margin, padding)
4. Sizing (width, height)
5. Typography
6. Visual (colors, borders, shadows)
7. Other (cursor, transitions)

```tsx
// ✅ Good
<div className="flex flex-col gap-4 p-6 w-full h-screen bg-white rounded-lg shadow-md">

// ❌ Bad - Random order
<div className="bg-white p-6 flex h-screen rounded-lg flex-col w-full gap-4 shadow-md">
```

### Component Variants
```tsx
// Sử dụng class-variance-authority cho variants
import { cva } from 'class-variance-authority';

const buttonVariants = cva(
  'base-classes',
  {
    variants: {
      variant: {
        default: 'bg-primary',
        secondary: 'bg-secondary',
      },
      size: {
        sm: 'text-sm px-2',
        md: 'text-base px-4',
      },
    },
  }
);
```

## 🧪 Testing

### Unit Tests (Coming Soon)
```bash
npm run test
```

### Linting
```bash
npm run lint
```

## 📝 Git Commit Messages

```
feat: Thêm tính năng mới
fix: Sửa lỗi
style: Thay đổi styling
refactor: Refactor code
docs: Cập nhật documentation
test: Thêm tests
chore: Cập nhật dependencies
```

## 🚀 Deployment

### Build Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 📚 Resources

- [React Docs](https://react.dev/)
- [TypeScript Docs](https://www.typescriptlang.org/docs/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Radix UI](https://www.radix-ui.com/docs/primitives/overview/introduction)
- [Vite Docs](https://vitejs.dev/)

## 🤝 Getting Help

1. Đọc documentation
2. Xem examples trong code hiện tại
3. Hỏi team members
4. Search trên Stack Overflow

## ✅ Checklist Before Commit

- [ ] Code runs without errors
- [ ] Types are properly defined
- [ ] No console.log statements
- [ ] Imports are organized
- [ ] Code follows style guide
- [ ] Components are properly documented
