import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { FileText, Mail, Lock, User, ArrowRight } from 'lucide-react';
import { apiService } from '@/services';
import { useToast } from '@/hooks/use-toast';

interface SignupPageProps {
  onNavigateToLogin: () => void;
}

export function SignupPage({ onNavigateToLogin }: SignupPageProps) {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const { toast } = useToast();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (password !== confirmPassword) {
      setError('Mật khẩu xác nhận không khớp!');
      return;
    }

    if (password.length < 8) {
      setError('Mật khẩu phải có ít nhất 8 ký tự');
      return;
    }
    
    setIsLoading(true);
    
    try {
      await apiService.register({ email, password, name });
      toast({
        title: 'Đăng ký thành công!',
        description: 'Vui lòng đăng nhập để tiếp tục.',
      });
      onNavigateToLogin();
    } catch (err: any) {
      const errorMsg = err.message || 'Đăng ký thất bại. Vui lòng thử lại.';
      setError(errorMsg);
      toast({
        title: 'Lỗi đăng ký',
        description: errorMsg,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex relative overflow-hidden">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-violet-50 via-purple-50 to-fuchsia-50 animate-gradient"></div>
      
      {/* Decorative elements */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-br from-violet-400/20 to-fuchsia-400/20 rounded-full blur-3xl"></div>
      <div className="absolute bottom-0 left-0 w-96 h-96 bg-gradient-to-br from-purple-400/20 to-pink-400/20 rounded-full blur-3xl"></div>

      {/* Form Section */}
      <div className="flex-1 flex items-center justify-center p-8 relative z-10">
        <div className="w-full max-w-md">
          {/* Logo & Title */}
          <div className="text-center mb-10">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-violet-600 to-fuchsia-600 rounded-2xl mb-4 shadow-lg shadow-violet-500/30">
              <FileText className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-4xl mb-2 bg-gradient-to-r from-violet-600 to-fuchsia-600 bg-clip-text text-transparent">
              Invoice Manager
            </h1>
            <p className="text-muted-foreground">Bắt đầu hành trình quản lý hóa đơn</p>
          </div>

          {/* Signup Card */}
          <div className="bg-white/80 backdrop-blur-xl rounded-3xl shadow-2xl shadow-black/10 border border-white/20 p-8">
            <div className="mb-8">
              <h2 className="text-2xl mb-2">Tạo tài khoản mới ✨</h2>
              <p className="text-muted-foreground">Chỉ mất 2 phút để bắt đầu</p>
            </div>

            <form onSubmit={handleSignup} className="space-y-5">
              {error && (
                <div className="p-3 rounded-lg bg-red-50 border border-red-200 text-red-600 text-sm">
                  {error}
                </div>
              )}
              <div className="grid grid-cols-1 gap-5">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-sm">Họ và tên</Label>
                  <div className="relative group">
                    <User className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-violet-600 transition-colors" />
                    <Input
                      id="name"
                      type="text"
                      placeholder="Nguyễn Văn A"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="pl-12 h-12 bg-white/50 border-gray-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 rounded-xl transition-all"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm">Địa chỉ Email</Label>
                  <div className="relative group">
                    <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-violet-600 transition-colors" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="your.email@company.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-12 h-12 bg-white/50 border-gray-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 rounded-xl transition-all"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm">Mật khẩu</Label>
                  <div className="relative group">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-violet-600 transition-colors" />
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••••"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      className="pl-12 h-12 bg-white/50 border-gray-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 rounded-xl transition-all"
                      required
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="confirm-password" className="text-sm">Xác nhận mật khẩu</Label>
                  <div className="relative group">
                    <Lock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground group-focus-within:text-violet-600 transition-colors" />
                    <Input
                      id="confirm-password"
                      type="password"
                      placeholder="••••••••••"
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      className="pl-12 h-12 bg-white/50 border-gray-200 focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 rounded-xl transition-all"
                      required
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">Tối thiểu 8 ký tự, bao gồm chữ và số</p>
                </div>
              </div>

              <Button 
                type="submit" 
                disabled={isLoading}
                className="w-full h-12 bg-gradient-to-r from-violet-600 to-fuchsia-600 hover:from-violet-700 hover:to-fuchsia-700 text-white rounded-xl shadow-lg shadow-violet-500/30 hover:shadow-xl hover:shadow-violet-500/40 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span>{isLoading ? 'Đang tạo tài khoản...' : 'Tạo tài khoản miễn phí'}</span>
                {!isLoading && <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />}
              </Button>

              {/* Divider */}
              <div className="relative my-6">
                <div className="absolute inset-0 flex items-center">
                  <div className="w-full border-t border-gray-200"></div>
                </div>
                <div className="relative flex justify-center text-sm">
                  <span className="px-4 bg-white/80 text-muted-foreground">hoặc</span>
                </div>
              </div>

              {/* Login link */}
              <div className="text-center">
                <p className="text-sm text-muted-foreground">
                  Đã có tài khoản?{' '}
                  <button
                    type="button"
                    onClick={onNavigateToLogin}
                    className="text-violet-600 hover:text-violet-700 transition-colors"
                  >
                    Đăng nhập ngay
                  </button>
                </p>
              </div>
            </form>
          </div>

          {/* Footer */}
          <p className="text-center text-xs text-muted-foreground mt-8">
            Bằng cách đăng ký, bạn đồng ý với{' '}
            <a href="#" className="hover:text-violet-600 transition-colors">Điều khoản</a>
            {' '}và{' '}
            <a href="#" className="hover:text-violet-600 transition-colors">Chính sách bảo mật</a>
          </p>
        </div>
      </div>
    </div>
  );
}
