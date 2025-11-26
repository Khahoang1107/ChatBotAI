import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Bell, 
  LogOut, 
  Users,
  FileText,
  DollarSign,
  TrendingUp,
  Activity,
  LayoutDashboard,
  Settings,
  BarChart3,
  FolderOpen,
  Shield,
  ChevronLeft,
  ChevronRight,
  ArrowUpRight,
  ArrowDownRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  Zap,
  Target,
  TrendingDown,
  ClipboardEdit,
  Type,
  AlignLeft,
  CheckSquare,
  Circle,
  List,
  Calendar,
  Upload,
  MousePointer,
  Trash2,
  Eye,
  Save,
  Plus,
  FileUp,
  Loader2
} from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { toast } from 'sonner';

interface AdminDashboardProps {
  user: {
    email: string;
    name: string;
  };
  onLogout: () => void;
}

export function AdminDashboard({ user, onLogout }: AdminDashboardProps) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [activeMenu, setActiveMenu] = useState('dashboard');
  const [invoicesSubMenu, setInvoicesSubMenu] = useState<'upload' | 'text'>('upload');
  
  // Form Builder State
  const [formFields, setFormFields] = useState<any[]>([]);
  const [formName, setFormName] = useState('Biểu mẫu mới');
  const [formDescription, setFormDescription] = useState('');
  
  // Upload File State
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'success' | 'error'>('idle');

  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard', badge: null },
    { id: 'users', icon: Users, label: 'Người dùng', badge: '1.2K' },
    { id: 'invoices', icon: FileText, label: 'Hóa đơn', badge: '45K' },
    { id: 'forms', icon: ClipboardEdit, label: 'Tạo biểu mẫu', badge: 'New' },
    { id: 'reports', icon: BarChart3, label: 'Báo cáo', badge: null },
    { id: 'files', icon: FolderOpen, label: 'Tài liệu', badge: null },
    { id: 'security', icon: Shield, label: 'Bảo mật', badge: '3' },
    { id: 'settings', icon: Settings, label: 'Cài đặt', badge: null },
  ];

  // Chart data
  const revenueData = [
    { month: 'T1', revenue: 4000, invoices: 240 },
    { month: 'T2', revenue: 3000, invoices: 139 },
    { month: 'T3', revenue: 2000, invoices: 980 },
    { month: 'T4', revenue: 2780, invoices: 390 },
    { month: 'T5', revenue: 1890, invoices: 480 },
    { month: 'T6', revenue: 2390, invoices: 380 },
    { month: 'T7', revenue: 3490, invoices: 430 },
  ];

  const userGrowthData = [
    { month: 'T1', users: 400 },
    { month: 'T2', users: 600 },
    { month: 'T3', users: 800 },
    { month: 'T4', users: 1000 },
    { month: 'T5', users: 900 },
    { month: 'T6', users: 1100 },
    { month: 'T7', users: 1234 },
  ];

  const categoryData = [
    { name: 'Điện', value: 400, color: '#3b82f6' },
    { name: 'Nước', value: 300, color: '#06b6d4' },
    { name: 'Internet', value: 200, color: '#8b5cf6' },
    { name: 'Điện thoại', value: 100, color: '#ec4899' },
  ];

  const taskData = [
    { name: 'Hoàn thành', value: 75, color: '#10b981' },
    { name: 'Đang xử lý', value: 15, color: '#f59e0b' },
    { name: 'Chờ duyệt', value: 10, color: '#3b82f6' },
  ];

  // Add field to form
  const addField = (type: string) => {
    const newField = {
      id: Date.now(),
      type,
      label: `${type === 'text' ? 'Trường text' : 
              type === 'textarea' ? 'Textarea' : 
              type === 'checkbox' ? 'Checkbox' : 
              type === 'radio' ? 'Radio' : 
              type === 'select' ? 'Select' : 
              type === 'date' ? 'Ngày tháng' : 
              type === 'file' ? 'Tải lên file' : 'Button'} ${formFields.length + 1}`,
      placeholder: type === 'text' || type === 'textarea' ? 'Nhập văn bản...' : '',
      required: false
    };
    setFormFields([...formFields, newField]);
  };

  // Remove field
  const removeField = (id: number) => {
    setFormFields(formFields.filter(field => field.id !== id));
  };

  // Save form
  const saveForm = () => {
    toast.success(`Đã lưu biểu mẫu: ${formName}\nSố trường: ${formFields.length}`);
  };

  // Handle file selection
  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      // Validate file type (only accept JSON, PDF, CSV, etc.)
      const allowedTypes = ['application/json', 'application/pdf', 'text/csv', 'application/vnd.ms-excel'];
      if (!allowedTypes.includes(file.type) && !file.name.endsWith('.xlsx')) {
        toast.error('Định dạng file không hợp lệ! Chỉ chấp nhận JSON, PDF, CSV, Excel');
        return;
      }
      
      // Validate file size (max 5MB)
      if (file.size > 5 * 1024 * 1024) {
        toast.error('File quá lớn! Kích thước tối đa là 5MB');
        return;
      }
      
      setUploadFile(file);
      setUploadStatus('idle');
      setUploadProgress(0);
    }
  };

  // Handle file upload
  const handleFileUpload = async () => {
    if (!uploadFile) {
      toast.error('Vui lòng chọn file trước khi upload!');
      return;
    }

    setUploadStatus('uploading');
    setUploadProgress(0);

    // Simulate upload progress
    const interval = setInterval(() => {
      setUploadProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);

    // Simulate server processing (2 seconds)
    setTimeout(() => {
      clearInterval(interval);
      
      // Random success/fail (90% success rate)
      const isSuccess = Math.random() > 0.1;
      
      if (isSuccess) {
        setUploadStatus('success');
        setUploadProgress(100);
        toast.success(`Upload thành công!\nFile: ${uploadFile.name}\nKích thước: ${(uploadFile.size / 1024).toFixed(2)} KB`, {
          duration: 5000,
        });
      } else {
        setUploadStatus('error');
        setUploadProgress(0);
        toast.error('Upload thất bại! Vui lòng thử lại.', {
          duration: 5000,
        });
      }
    }, 2000);
  };

  // Clear upload
  const clearUpload = () => {
    setUploadFile(null);
    setUploadStatus('idle');
    setUploadProgress(0);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-gray-50 to-zinc-50 flex">
      {/* Sidebar */}
      <aside className={`${sidebarCollapsed ? 'w-20' : 'w-64'} bg-white/80 backdrop-blur-xl border-r border-gray-200 transition-all duration-300 flex flex-col fixed h-screen z-40`}>
        {/* Logo Section */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 via-purple-500 to-pink-500 rounded-xl flex items-center justify-center shadow-lg flex-shrink-0 animate-pulse hover:scale-110 transition-transform duration-300 relative">
              <div className="absolute inset-0 bg-gradient-to-br from-blue-400 via-purple-400 to-pink-400 rounded-xl blur-sm opacity-50"></div>
              <FileText className="w-5 h-5 text-white relative z-10" />
            </div>
            {!sidebarCollapsed && (
              <div className="overflow-hidden">
                <h1 className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 bg-clip-text text-transparent whitespace-nowrap">
                  Invoice Manager
                </h1>
                <p className="text-xs text-muted-foreground">Admin Panel</p>
              </div>
            )}
          </div>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {menuItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeMenu === item.id;
            
            // Color schemes for each menu item
            const colorSchemes: Record<string, { gradient: string; icon: string; iconBg: string; activeBg: string }> = {
              dashboard: { 
                gradient: 'from-blue-500 to-cyan-500', 
                icon: 'text-blue-600',
                iconBg: 'bg-gradient-to-br from-blue-100 to-cyan-100',
                activeBg: 'bg-gradient-to-r from-blue-600 to-cyan-600'
              },
              users: { 
                gradient: 'from-purple-500 to-pink-500', 
                icon: 'text-purple-600',
                iconBg: 'bg-gradient-to-br from-purple-100 to-pink-100',
                activeBg: 'bg-gradient-to-r from-purple-600 to-pink-600'
              },
              invoices: { 
                gradient: 'from-emerald-500 to-teal-500', 
                icon: 'text-emerald-600',
                iconBg: 'bg-gradient-to-br from-emerald-100 to-teal-100',
                activeBg: 'bg-gradient-to-r from-emerald-600 to-teal-600'
              },
              forms: { 
                gradient: 'from-green-500 to-lime-500', 
                icon: 'text-green-600',
                iconBg: 'bg-gradient-to-br from-green-100 to-lime-100',
                activeBg: 'bg-gradient-to-r from-green-600 to-lime-600'
              },
              reports: { 
                gradient: 'from-orange-500 to-amber-500', 
                icon: 'text-orange-600',
                iconBg: 'bg-gradient-to-br from-orange-100 to-amber-100',
                activeBg: 'bg-gradient-to-r from-orange-600 to-amber-600'
              },
              files: { 
                gradient: 'from-indigo-500 to-blue-500', 
                icon: 'text-indigo-600',
                iconBg: 'bg-gradient-to-br from-indigo-100 to-blue-100',
                activeBg: 'bg-gradient-to-r from-indigo-600 to-blue-600'
              },
              security: { 
                gradient: 'from-red-500 to-rose-500', 
                icon: 'text-red-600',
                iconBg: 'bg-gradient-to-br from-red-100 to-rose-100',
                activeBg: 'bg-gradient-to-r from-red-600 to-rose-600'
              },
              settings: { 
                gradient: 'from-slate-500 to-gray-500', 
                icon: 'text-slate-600',
                iconBg: 'bg-gradient-to-br from-slate-100 to-gray-100',
                activeBg: 'bg-gradient-to-r from-slate-600 to-gray-600'
              },
            };
            
            const colors = colorSchemes[item.id] || colorSchemes.dashboard;
            
            return (
              <button
                key={item.id}
                onClick={() => setActiveMenu(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group relative ${
                  isActive
                    ? `${colors.activeBg} text-white shadow-lg hover:shadow-xl`
                    : 'hover:bg-gray-50 text-gray-700'
                }`}
              >
                {/* Icon with background */}
                <div className={`w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0 transition-all duration-200 ${
                  isActive 
                    ? 'bg-white/20 shadow-md' 
                    : `${colors.iconBg} group-hover:scale-110 group-hover:shadow-md`
                }`}>
                  <Icon className={`w-5 h-5 ${isActive ? 'text-white' : colors.icon}`} />
                </div>
                
                {!sidebarCollapsed && (
                  <>
                    <span className="flex-1 text-left text-sm">{item.label}</span>
                    {item.badge && (
                      <Badge 
                        variant={isActive ? "secondary" : "outline"} 
                        className={`text-xs h-5 transition-all duration-200 ${
                          isActive 
                            ? 'bg-white/20 text-white border-white/30' 
                            : `bg-gradient-to-r ${colors.gradient} text-white border-0`
                        }`}
                      >
                        {item.badge}
                      </Badge>
                    )}
                  </>
                )}
                {sidebarCollapsed && item.badge && (
                  <span className={`absolute -top-1 -right-1 w-5 h-5 bg-gradient-to-r ${colors.gradient} text-white text-xs rounded-full flex items-center justify-center shadow-lg`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* User Section */}
        <div className="p-3 border-t border-gray-200">
          {!sidebarCollapsed ? (
            <div className="bg-gradient-to-r from-slate-50 to-zinc-50 rounded-xl p-3">
              <div className="flex items-center gap-3 mb-3">
                <Avatar className="w-10 h-10 border-2 border-white shadow-md">
                  <AvatarImage src="" />
                  <AvatarFallback className="bg-gradient-to-br from-slate-600 to-zinc-700 text-white">
                    {user.name.charAt(0).toUpperCase()}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-1">
                    <p className="text-sm truncate">{user.name}</p>
                    <Badge variant="secondary" className="text-xs h-4 px-1">Admin</Badge>
                  </div>
                  <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                </div>
              </div>
              <Button 
                onClick={onLogout}
                variant="outline" 
                size="sm" 
                className="w-full h-9 hover:bg-red-50 hover:text-red-600 hover:border-red-300 transition-colors"
              >
                <LogOut className="w-4 h-4 mr-2" />
                Đăng xuất
              </Button>
            </div>
          ) : (
            <Button 
              onClick={onLogout}
              variant="ghost" 
              size="icon"
              className="w-full hover:bg-red-50 hover:text-red-600"
            >
              <LogOut className="w-5 h-5" />
            </Button>
          )}
        </div>

        {/* Toggle Button */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="absolute -right-3 top-20 w-6 h-6 bg-white border border-gray-200 rounded-full flex items-center justify-center shadow-md hover:shadow-lg transition-all hover:scale-110"
        >
          {sidebarCollapsed ? (
            <ChevronRight className="w-4 h-4 text-gray-600" />
          ) : (
            <ChevronLeft className="w-4 h-4 text-gray-600" />
          )}
        </button>
      </aside>

      {/* Main Content */}
      <div className={`flex-1 ${sidebarCollapsed ? 'ml-20' : 'ml-64'} transition-all duration-300`}>
        {/* Header */}
        <header className="bg-white/80 backdrop-blur-xl border-b border-gray-200 sticky top-0 z-30">
          <div className="px-6 py-4 flex items-center justify-between border-b bg-gradient-to-r from-white via-gray-50/50 to-white backdrop-blur-sm">
            {/* Page Title */}
            <div className="space-y-1">
              <h2 className="text-3xl bg-gradient-to-r from-blue-600 via-violet-600 to-purple-600 bg-clip-text text-transparent animate-gradient">
                {activeMenu === 'dashboard' && 'Dashboard Quản Trị'}
                {activeMenu === 'users' && 'Quản lý Người dùng'}
                {activeMenu === 'invoices' && 'Quản lý Hóa đơn'}
                {activeMenu === 'forms' && 'Tạo Biểu mẫu'}
                {activeMenu === 'reports' && 'Báo cáo & Phân tích'}
                {activeMenu === 'files' && 'Quản lý Tệp tin'}
                {activeMenu === 'security' && 'Bảo mật & Quyền truy cập'}
                {activeMenu === 'settings' && 'Cài đặt Hệ thống'}
              </h2>
              <p className="text-sm text-muted-foreground flex items-center gap-2">
                {activeMenu === 'dashboard' && (
                  <>
                    <Activity className="w-4 h-4 text-blue-500" />
                    Tổng quan hệ thống và hoạt động
                  </>
                )}
                {activeMenu === 'users' && (
                  <>
                    <Users className="w-4 h-4 text-purple-500" />
                    Danh sách và quản lý tất cả người dùng
                  </>
                )}
                {activeMenu === 'invoices' && (
                  <>
                    <FileText className="w-4 h-4 text-emerald-500" />
                    Theo dõi và quản lý tất cả hóa đơn
                  </>
                )}
                {activeMenu === 'forms' && (
                  <>
                    <ClipboardEdit className="w-4 h-4 text-green-500" />
                    Tạo và tùy chỉnh biểu mẫu tùy chỉnh
                  </>
                )}
                {activeMenu === 'reports' && (
                  <>
                    <BarChart3 className="w-4 h-4 text-orange-500" />
                    Thống kê và phân tích dữ liệu
                  </>
                )}
                {activeMenu === 'files' && (
                  <>
                    <FolderOpen className="w-4 h-4 text-indigo-500" />
                    Quản lý các file và tài liệu đã upload
                  </>
                )}
                {activeMenu === 'security' && (
                  <>
                    <Shield className="w-4 h-4 text-red-500" />
                    Quản lý bảo mật và logs hoạt động
                  </>
                )}
                {activeMenu === 'settings' && (
                  <>
                    <Settings className="w-4 h-4 text-slate-500" />
                    Cấu hình và tùy chỉnh hệ thống
                  </>
                )}
              </p>
            </div>

            {/* Right Side */}
            <div className="flex items-center gap-3">
              {/* Notifications */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon" className="relative hover:bg-gradient-to-br hover:from-blue-50 hover:to-purple-50 rounded-xl transition-all duration-200 hover:scale-105">
                    <Bell className="h-5 w-5 text-gray-700" />
                    <Badge className="absolute -top-1 -right-1 w-5 h-5 flex items-center justify-center p-0 bg-gradient-to-r from-red-500 to-rose-600 border-2 border-white shadow-lg animate-pulse">
                      5
                    </Badge>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-80 shadow-xl border-gray-200">
                  <DropdownMenuLabel className="flex items-center gap-2 text-base py-3 bg-gradient-to-r from-blue-50 to-purple-50">
                    <Bell className="w-4 h-4 text-blue-600" />
                    Thông báo quản trị
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="p-3 hover:bg-blue-50 cursor-pointer">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-green-500 to-emerald-600 flex items-center justify-center flex-shrink-0">
                        <Users className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex flex-col gap-1 flex-1">
                        <p className="text-sm">User mới đăng ký</p>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          10 phút trước
                        </p>
                      </div>
                    </div>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="p-3 hover:bg-purple-50 cursor-pointer">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center flex-shrink-0">
                        <AlertCircle className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex flex-col gap-1 flex-1">
                        <p className="text-sm">Hệ thống cần cập nhật</p>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          30 phút trước
                        </p>
                      </div>
                    </div>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="p-3 hover:bg-blue-50 cursor-pointer">
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-600 flex items-center justify-center flex-shrink-0">
                        <FileText className="w-4 h-4 text-white" />
                      </div>
                      <div className="flex flex-col gap-1 flex-1">
                        <p className="text-sm">45 hóa đơn mới</p>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          1 giờ trước
                        </p>
                      </div>
                    </div>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="p-2 text-center text-blue-600 hover:bg-blue-50 cursor-pointer justify-center">
                    Xem tất cả thông báo
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>

              {/* User Avatar */}
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" className="flex items-center gap-3 hover:bg-gradient-to-br hover:from-blue-50 hover:to-purple-50 rounded-xl px-3 py-2 transition-all duration-200 hover:scale-105">
                    <div className="text-right hidden md:block">
                      <p className="text-sm">{user.name}</p>
                      <p className="text-xs text-muted-foreground">{user.email}</p>
                    </div>
                    <Avatar className="w-10 h-10 border-2 border-gradient-to-br from-blue-500 to-purple-500 shadow-md">
                      <AvatarImage src="" />
                      <AvatarFallback className="bg-gradient-to-br from-blue-500 via-violet-500 to-purple-500 text-white">
                        {user.name.charAt(0)}
                      </AvatarFallback>
                    </Avatar>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-64 shadow-xl border-gray-200">
                  <DropdownMenuLabel className="py-3 bg-gradient-to-r from-blue-50 to-purple-50">
                    <div className="flex items-center gap-3">
                      <Avatar className="w-12 h-12 border-2 border-white shadow-md">
                        <AvatarFallback className="bg-gradient-to-br from-blue-500 via-violet-500 to-purple-500 text-white text-lg">
                          {user.name.charAt(0)}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm">{user.name}</p>
                        <p className="text-xs text-muted-foreground">{user.email}</p>
                        <Badge className="mt-1 bg-gradient-to-r from-blue-600 to-purple-600 text-white text-xs">
                          Admin
                        </Badge>
                      </div>
                    </div>
                  </DropdownMenuLabel>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem className="cursor-pointer hover:bg-blue-50">
                    <Settings className="mr-2 h-4 w-4 text-blue-600" />
                    <span>Cài đặt tài khoản</span>
                  </DropdownMenuItem>
                  <DropdownMenuItem className="cursor-pointer hover:bg-purple-50">
                    <Shield className="mr-2 h-4 w-4 text-purple-600" />
                    <span>Bảo mật</span>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem 
                    onClick={onLogout}
                    className="cursor-pointer hover:bg-red-50 text-red-600"
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    <span>Đăng xuất</span>
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <main className="p-6">
          {activeMenu === 'users' ? (
            /* Users Management */
            <div className="space-y-6">
              {/* Users Header */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b bg-gradient-to-r from-purple-50 to-pink-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                          <Users className="w-5 h-5 text-white" />
                        </div>
                        Quản lý người dùng
                      </CardTitle>
                      <CardDescription>Danh sách và quản lý tất cả người dùng trong hệ thống</CardDescription>
                    </div>
                    <Button className="bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white shadow-lg">
                      <Plus className="w-4 h-4 mr-2" />
                      Thêm người dùng
                    </Button>
                  </div>
                </CardHeader>
              </Card>

              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Tổng users</p>
                        <p className="text-2xl">1,234</p>
                      </div>
                      <Users className="w-8 h-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Admins</p>
                        <p className="text-2xl">12</p>
                      </div>
                      <Shield className="w-8 h-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Active</p>
                        <p className="text-2xl">1,180</p>
                      </div>
                      <CheckCircle2 className="w-8 h-8 text-purple-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-orange-50 to-red-50 border-orange-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Inactive</p>
                        <p className="text-2xl">54</p>
                      </div>
                      <AlertCircle className="w-8 h-8 text-orange-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Users Table */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b">
                  <div className="flex items-center justify-between">
                    <CardTitle>Danh sách người dùng</CardTitle>
                    <div className="flex gap-2">
                      <input
                        type="search"
                        placeholder="Tìm kiếm..."
                        className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-500"
                      />
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50 border-b">
                        <tr>
                          <th className="px-6 py-3 text-left text-xs uppercase tracking-wider text-gray-500">User</th>
                          <th className="px-6 py-3 text-left text-xs uppercase tracking-wider text-gray-500">Email</th>
                          <th className="px-6 py-3 text-left text-xs uppercase tracking-wider text-gray-500">Role</th>
                          <th className="px-6 py-3 text-left text-xs uppercase tracking-wider text-gray-500">Status</th>
                          <th className="px-6 py-3 text-left text-xs uppercase tracking-wider text-gray-500">Joined</th>
                          <th className="px-6 py-3 text-left text-xs uppercase tracking-wider text-gray-500">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {['Nguyễn Văn A', 'Trần Thị B', 'Lê Văn C', 'Phạm Thị D', 'Hoàng Văn E'].map((name, idx) => (
                          <tr key={idx} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex items-center gap-3">
                                <Avatar className="w-10 h-10">
                                  <AvatarFallback className="bg-gradient-to-br from-purple-500 to-pink-500 text-white">
                                    {name.charAt(0)}
                                  </AvatarFallback>
                                </Avatar>
                                <span className="text-sm">{name}</span>
                              </div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {name.toLowerCase().replace(/\s+/g, '')}@email.com
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Badge variant={idx === 0 ? 'default' : 'outline'} className={idx === 0 ? 'bg-purple-600' : ''}>
                                {idx === 0 ? 'Admin' : 'User'}
                              </Badge>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <Badge variant="outline" className={idx < 4 ? 'border-green-500 text-green-700' : 'border-gray-400 text-gray-700'}>
                                {idx < 4 ? 'Active' : 'Inactive'}
                              </Badge>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600">
                              {new Date(2024, 0, idx + 1).toLocaleDateString('vi-VN')}
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                              <div className="flex gap-2">
                                <Button variant="ghost" size="sm" className="hover:bg-blue-50">
                                  <Eye className="w-4 h-4" />
                                </Button>
                                <Button variant="ghost" size="sm" className="hover:bg-purple-50">
                                  <Settings className="w-4 h-4" />
                                </Button>
                                <Button variant="ghost" size="sm" className="hover:bg-red-50">
                                  <Trash2 className="w-4 h-4 text-red-600" />
                                </Button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : activeMenu === 'invoices' ? (
            /* Invoices Management */
            <div className="space-y-6">
              {/* Invoices Header with Tabs */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b bg-gradient-to-r from-emerald-50 to-teal-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center">
                          <FileText className="w-5 h-5 text-white" />
                        </div>
                        Quản lý hóa đơn
                      </CardTitle>
                      <CardDescription>Tạo và quản lý hóa đơn bằng 2 cách: Upload file hoặc Nhập text</CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-0">
                  {/* Tabs Navigation */}
                  <div className="flex border-b">
                    <button
                      onClick={() => setInvoicesSubMenu('upload')}
                      className={`flex-1 px-6 py-4 text-sm transition-all ${
                        invoicesSubMenu === 'upload'
                          ? 'bg-gradient-to-r from-emerald-50 to-teal-50 border-b-2 border-emerald-600 text-emerald-700'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-center gap-2">
                        <Upload className="w-4 h-4" />
                        <span>Upload File</span>
                      </div>
                    </button>
                    <button
                      onClick={() => setInvoicesSubMenu('text')}
                      className={`flex-1 px-6 py-4 text-sm transition-all ${
                        invoicesSubMenu === 'text'
                          ? 'bg-gradient-to-r from-emerald-50 to-teal-50 border-b-2 border-emerald-600 text-emerald-700'
                          : 'text-gray-600 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center justify-center gap-2">
                        <Type className="w-4 h-4" />
                        <span>Nhập Text</span>
                      </div>
                    </button>
                  </div>
                </CardContent>
              </Card>

              {/* Upload File Tab */}
              {invoicesSubMenu === 'upload' && (
                <div className="space-y-6">
                  {/* Upload Area */}
                  <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                    <CardHeader className="border-b">
                      <CardTitle className="flex items-center gap-2">
                        <Upload className="w-5 h-5 text-emerald-600" />
                        Upload File Hóa Đơn
                      </CardTitle>
                      <CardDescription>
                        Tải lên file hóa đơn (PDF, CSV, Excel, JSON) để xem cấu trúc và xử lý
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-6">
                      <div className="border-2 border-dashed border-emerald-300 rounded-lg p-12 text-center hover:border-emerald-500 hover:bg-emerald-50/50 transition-all cursor-pointer">
                        <Upload className="w-16 h-16 mx-auto mb-4 text-emerald-400" />
                        <p className="text-sm mb-2">Kéo thả file vào đây hoặc click để chọn</p>
                        <p className="text-xs text-muted-foreground">PDF, CSV, Excel, JSON (tối đa 10MB)</p>
                        <Button className="mt-4 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white">
                          <FileUp className="w-4 h-4 mr-2" />
                          Chọn file
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  {/* File Structure Preview */}
                  <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                    <CardHeader className="border-b">
                      <CardTitle className="flex items-center gap-2">
                        <Eye className="w-5 h-5 text-blue-600" />
                        Xem Cấu Trúc File
                      </CardTitle>
                      <CardDescription>
                        Cấu trúc dữ liệu được phân tích từ file
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-6">
                      <div className="bg-gray-900 rounded-lg p-4 text-green-400 font-mono text-sm">
                        <pre className="overflow-x-auto">
{`{
  "invoice_id": "INV-001",
  "customer": {
    "name": "Công ty ABC",
    "email": "abc@company.com",
    "address": "123 Đường XYZ, TP.HCM"
  },
  "items": [
    {
      "name": "Sản phẩm A",
      "quantity": 2,
      "price": 500000,
      "total": 1000000
    },
    {
      "name": "Sản phẩm B",
      "quantity": 1,
      "price": 800000,
      "total": 800000
    }
  ],
  "subtotal": 1800000,
  "tax": 180000,
  "total": 1980000,
  "status": "pending",
  "created_at": "2024-11-24"
}`}
                        </pre>
                      </div>
                      <div className="mt-4 flex gap-2">
                        <Button variant="outline">
                          <Eye className="w-4 h-4 mr-2" />
                          Xem chi tiết
                        </Button>
                        <Button className="bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white">
                          <CheckCircle2 className="w-4 h-4 mr-2" />
                          Xác nhận & Lưu
                        </Button>
                      </div>
                    </CardContent>
                  </Card>

                  {/* Recently Uploaded */}
                  <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                    <CardHeader className="border-b">
                      <CardTitle>File đã upload gần đây</CardTitle>
                    </CardHeader>
                    <CardContent className="p-6">
                      <div className="space-y-3">
                        {[
                          { name: 'invoice_2024_001.pdf', size: '2.4 MB', date: '24/11/2024 10:30', status: 'success' },
                          { name: 'invoices_batch.csv', size: '856 KB', date: '24/11/2024 09:15', status: 'success' },
                          { name: 'invoice_data.xlsx', size: '1.2 MB', date: '23/11/2024 16:45', status: 'processing' },
                        ].map((file, idx) => (
                          <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                            <div className="flex items-center gap-3">
                              <div className="w-10 h-10 bg-gradient-to-br from-emerald-100 to-teal-100 rounded-lg flex items-center justify-center">
                                <FileText className="w-5 h-5 text-emerald-600" />
                              </div>
                              <div>
                                <p className="text-sm">{file.name}</p>
                                <p className="text-xs text-muted-foreground">{file.size} • {file.date}</p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <Badge variant="outline" className={
                                file.status === 'success' ? 'border-green-500 text-green-700' : 'border-yellow-500 text-yellow-700'
                              }>
                                {file.status === 'success' ? 'Thành công' : 'Đang xử lý'}
                              </Badge>
                              <Button variant="ghost" size="sm">
                                <Eye className="w-4 h-4" />
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}

              {/* Text Input Tab */}
              {invoicesSubMenu === 'text' && (
                <div className="space-y-6">
                  {/* Invoice Form */}
                  <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                    <CardHeader className="border-b">
                      <CardTitle className="flex items-center gap-2">
                        <Type className="w-5 h-5 text-emerald-600" />
                        Nhập Thông Tin Hóa Đơn
                      </CardTitle>
                      <CardDescription>
                        Điền đầy đủ thông tin để tạo hóa đơn mới
                      </CardDescription>
                    </CardHeader>
                    <CardContent className="p-6 space-y-6">
                      {/* Customer Information */}
                      <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-emerald-700 flex items-center gap-2">
                          <Users className="w-4 h-4" />
                          Thông tin khách hàng
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <label className="text-sm mb-2 block">Tên khách hàng *</label>
                            <input
                              type="text"
                              placeholder="Công ty ABC"
                              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="text-sm mb-2 block">Email</label>
                            <input
                              type="email"
                              placeholder="customer@company.com"
                              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                          </div>
                          <div className="md:col-span-2">
                            <label className="text-sm mb-2 block">Địa chỉ</label>
                            <input
                              type="text"
                              placeholder="123 Đường XYZ, Quận 1, TP.HCM"
                              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Invoice Details */}
                      <div className="space-y-4">
                        <h3 className="text-sm font-semibold text-emerald-700 flex items-center gap-2">
                          <FileText className="w-4 h-4" />
                          Chi tiết hóa đơn
                        </h3>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div>
                            <label className="text-sm mb-2 block">Mã hóa đơn *</label>
                            <input
                              type="text"
                              placeholder="INV-001"
                              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="text-sm mb-2 block">Ngày tạo *</label>
                            <input
                              type="date"
                              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                          </div>
                          <div>
                            <label className="text-sm mb-2 block">Hạn thanh toán</label>
                            <input
                              type="date"
                              className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                            />
                          </div>
                        </div>
                      </div>

                      {/* Items */}
                      <div className="space-y-4">
                        <div className="flex items-center justify-between">
                          <h3 className="text-sm font-semibold text-emerald-700 flex items-center gap-2">
                            <List className="w-4 h-4" />
                            Danh sách sản phẩm/dịch vụ
                          </h3>
                          <Button size="sm" variant="outline" className="text-emerald-600 border-emerald-600 hover:bg-emerald-50">
                            <Plus className="w-4 h-4 mr-1" />
                            Thêm dòng
                          </Button>
                        </div>
                        
                        <div className="space-y-3">
                          {[1, 2].map((item) => (
                            <div key={item} className="grid grid-cols-12 gap-3 p-4 bg-gray-50 rounded-lg">
                              <div className="col-span-5">
                                <input
                                  type="text"
                                  placeholder="Tên sản phẩm/dịch vụ"
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                                />
                              </div>
                              <div className="col-span-2">
                                <input
                                  type="number"
                                  placeholder="Số lượng"
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                                />
                              </div>
                              <div className="col-span-2">
                                <input
                                  type="number"
                                  placeholder="Đơn giá"
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500"
                                />
                              </div>
                              <div className="col-span-2">
                                <input
                                  type="text"
                                  placeholder="Thành tiền"
                                  className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm bg-gray-100"
                                  disabled
                                />
                              </div>
                              <div className="col-span-1 flex items-center justify-center">
                                <Button variant="ghost" size="sm" className="hover:bg-red-50 hover:text-red-600">
                                  <Trash2 className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {/* Summary */}
                      <div className="space-y-3 p-4 bg-emerald-50 rounded-lg border border-emerald-200">
                        <div className="flex justify-between text-sm">
                          <span>Tạm tính:</span>
                          <span className="font-semibold">₫0</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Thuế VAT (10%):</span>
                          <span className="font-semibold">₫0</span>
                        </div>
                        <div className="flex justify-between text-lg border-t border-emerald-300 pt-3">
                          <span>Tổng cộng:</span>
                          <span className="font-bold text-emerald-700">₫0</span>
                        </div>
                      </div>

                      {/* Notes */}
                      <div>
                        <label className="text-sm mb-2 block">Ghi chú</label>
                        <textarea
                          rows={3}
                          placeholder="Thêm ghi chú cho hóa đơn..."
                          className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-emerald-500"
                        />
                      </div>

                      {/* Actions */}
                      <div className="flex gap-3 pt-4 border-t">
                        <Button className="flex-1 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white">
                          <Save className="w-4 h-4 mr-2" />
                          Lưu hóa đơn
                        </Button>
                        <Button variant="outline" className="flex-1">
                          <Eye className="w-4 h-4 mr-2" />
                          Xem trước
                        </Button>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>
          ) : activeMenu === 'forms' ? (
            /* Form Builder */
            <div className="space-y-6">
              {/* Form Builder Header */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b bg-gradient-to-r from-green-50 to-lime-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-lime-600 rounded-lg flex items-center justify-center">
                          <ClipboardEdit className="w-5 h-5 text-white" />
                        </div>
                        Công cụ tạo biểu mẫu
                      </CardTitle>
                      <CardDescription>Tạo và tùy chỉnh biểu mẫu với các trường dữ liệu</CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button onClick={saveForm} className="bg-gradient-to-r from-green-600 to-lime-600 hover:from-green-700 hover:to-lime-700 text-white shadow-lg">
                        <Save className="w-4 h-4 mr-2" />
                        Lưu biểu mẫu
                      </Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div>
                      <label className="text-sm mb-2 block">Tên biểu mẫu</label>
                      <input
                        type="text"
                        value={formName}
                        onChange={(e) => setFormName(e.target.value)}
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                    <div>
                      <label className="text-sm mb-2 block">Mô tả</label>
                      <input
                        type="text"
                        value={formDescription}
                        onChange={(e) => setFormDescription(e.target.value)}
                        placeholder="Mô tả ngắn về biểu mẫu..."
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Toolbar */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b">
                  <CardTitle className="text-lg flex items-center gap-2">
                    <Plus className="w-5 h-5 text-green-600" />
                    Thêm trường dữ liệu
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <Button
                      onClick={() => addField('text')}
                      variant="outline"
                      className="h-auto py-4 flex flex-col gap-2 hover:bg-blue-50 hover:border-blue-300 transition-all"
                    >
                      <Type className="w-6 h-6 text-blue-600" />
                      <span className="text-sm">Text</span>
                    </Button>
                    <Button
                      onClick={() => addField('textarea')}
                      variant="outline"
                      className="h-auto py-4 flex flex-col gap-2 hover:bg-purple-50 hover:border-purple-300 transition-all"
                    >
                      <AlignLeft className="w-6 h-6 text-purple-600" />
                      <span className="text-sm">Textarea</span>
                    </Button>
                    <Button
                      onClick={() => addField('checkbox')}
                      variant="outline"
                      className="h-auto py-4 flex flex-col gap-2 hover:bg-green-50 hover:border-green-300 transition-all"
                    >
                      <CheckSquare className="w-6 h-6 text-green-600" />
                      <span className="text-sm">Checkbox</span>
                    </Button>
                    <Button
                      onClick={() => addField('radio')}
                      variant="outline"
                      className="h-auto py-4 flex flex-col gap-2 hover:bg-pink-50 hover:border-pink-300 transition-all"
                    >
                      <Circle className="w-6 h-6 text-pink-600" />
                      <span className="text-sm">Radio</span>
                    </Button>
                    <Button
                      onClick={() => addField('select')}
                      variant="outline"
                      className="h-auto py-4 flex flex-col gap-2 hover:bg-orange-50 hover:border-orange-300 transition-all"
                    >
                      <List className="w-6 h-6 text-orange-600" />
                      <span className="text-sm">Select</span>
                    </Button>
                    <Button
                      onClick={() => addField('date')}
                      variant="outline"
                      className="h-auto py-4 flex flex-col gap-2 hover:bg-indigo-50 hover:border-indigo-300 transition-all"
                    >
                      <Calendar className="w-6 h-6 text-indigo-600" />
                      <span className="text-sm">Ngày tháng</span>
                    </Button>
                    <Button
                      onClick={() => addField('file')}
                      variant="outline"
                      className="h-auto py-4 flex flex-col gap-2 hover:bg-teal-50 hover:border-teal-300 transition-all"
                    >
                      <Upload className="w-6 h-6 text-teal-600" />
                      <span className="text-sm">File Upload</span>
                    </Button>
                    <Button
                      onClick={() => addField('button')}
                      variant="outline"
                      className="h-auto py-4 flex flex-col gap-2 hover:bg-red-50 hover:border-red-300 transition-all"
                    >
                      <MousePointer className="w-6 h-6 text-red-600" />
                      <span className="text-sm">Button</span>
                    </Button>
                  </div>
                </CardContent>
              </Card>

              {/* Form Preview */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-cyan-50">
                  <CardTitle className="flex items-center gap-2">
                    <Eye className="w-5 h-5 text-blue-600" />
                    Xem trước biểu mẫu
                  </CardTitle>
                  <CardDescription>
                    {formFields.length > 0 
                      ? `Đã thêm ${formFields.length} trường dữ liệu` 
                      : 'Chưa có trường dữ liệu nào. Hãy thêm từ công cụ bên trên.'}
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  {formFields.length === 0 ? (
                    <div className="text-center py-12 text-muted-foreground">
                      <ClipboardEdit className="w-16 h-16 mx-auto mb-4 opacity-20" />
                      <p>Nhấn vào các nút bên trên để thêm trường vào biểu mẫu</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {formFields.map((field, idx) => (
                        <div key={field.id} className="p-4 border border-gray-200 rounded-lg bg-gradient-to-r from-gray-50 to-white hover:shadow-md transition-shadow group">
                          <div className="flex items-start justify-between mb-3">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-1">
                                <Badge variant="outline" className="text-xs">
                                  {field.type}
                                </Badge>
                                <span className="text-sm">{field.label}</span>
                              </div>
                            </div>
                            <Button
                              onClick={() => removeField(field.id)}
                              variant="ghost"
                              size="icon"
                              className="opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-50 hover:text-red-600"
                            >
                              <Trash2 className="w-4 h-4" />
                            </Button>
                          </div>
                          
                          {/* Field Preview */}
                          {field.type === 'text' && (
                            <input
                              type="text"
                              placeholder={field.placeholder}
                              className="w-full px-3 py-2 border border-gray-200 rounded-lg"
                              disabled
                            />
                          )}
                          {field.type === 'textarea' && (
                            <textarea
                              placeholder={field.placeholder}
                              rows={3}
                              className="w-full px-3 py-2 border border-gray-200 rounded-lg"
                              disabled
                            />
                          )}
                          {field.type === 'checkbox' && (
                            <div className="flex items-center gap-2">
                              <input type="checkbox" id={`field-${field.id}`} disabled />
                              <label htmlFor={`field-${field.id}`} className="text-sm">Checkbox option</label>
                            </div>
                          )}
                          {field.type === 'radio' && (
                            <div className="space-y-2">
                              <div className="flex items-center gap-2">
                                <input type="radio" name={`radio-${field.id}`} disabled />
                                <label className="text-sm">Tùy chọn 1</label>
                              </div>
                              <div className="flex items-center gap-2">
                                <input type="radio" name={`radio-${field.id}`} disabled />
                                <label className="text-sm">Tùy chọn 2</label>
                              </div>
                            </div>
                          )}
                          {field.type === 'select' && (
                            <select className="w-full px-3 py-2 border border-gray-200 rounded-lg" disabled>
                              <option>Chọn một tùy chọn...</option>
                              <option>Tùy chọn 1</option>
                              <option>Tùy chọn 2</option>
                            </select>
                          )}
                          {field.type === 'date' && (
                            <input
                              type="date"
                              className="w-full px-3 py-2 border border-gray-200 rounded-lg"
                              disabled
                            />
                          )}
                          {field.type === 'file' && (
                            <input
                              type="file"
                              className="w-full px-3 py-2 border border-gray-200 rounded-lg"
                              disabled
                            />
                          )}
                          {field.type === 'button' && (
                            <Button variant="default" disabled>
                              {field.label}
                            </Button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Upload Form Template */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b bg-gradient-to-r from-violet-50 to-purple-50">
                  <CardTitle className="flex items-center gap-2">
                    <FileUp className="w-5 h-5 text-violet-600" />
                    Upload Biểu Mẫu
                  </CardTitle>
                  <CardDescription>
                    Tải lên file biểu mẫu (JSON, PDF, CSV, Excel) - Tối đa 5MB
                  </CardDescription>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="space-y-4">
                    {/* File Input Area */}
                    <div className={`border-2 border-dashed rounded-lg p-8 text-center transition-all ${
                      uploadStatus === 'idle' 
                        ? 'border-gray-300 hover:border-violet-400 hover:bg-violet-50/50' 
                        : uploadStatus === 'uploading'
                        ? 'border-blue-400 bg-blue-50/50'
                        : uploadStatus === 'success'
                        ? 'border-green-400 bg-green-50/50'
                        : 'border-red-400 bg-red-50/50'
                    }`}>
                      <input
                        type="file"
                        id="form-upload"
                        accept=".json,.pdf,.csv,.xlsx,.xls"
                        onChange={handleFileSelect}
                        className="hidden"
                        disabled={uploadStatus === 'uploading'}
                      />
                      
                      {uploadStatus === 'idle' && !uploadFile && (
                        <label htmlFor="form-upload" className="cursor-pointer">
                          <FileUp className="w-16 h-16 mx-auto mb-4 text-violet-400" />
                          <p className="text-sm mb-2">Click để chọn file hoặc kéo thả vào đây</p>
                          <p className="text-xs text-muted-foreground">JSON, PDF, CSV, Excel (tối đa 5MB)</p>
                        </label>
                      )}
                      
                      {uploadFile && uploadStatus !== 'uploading' && (
                        <div className="space-y-3">
                          <div className={`flex items-center justify-center gap-3 ${
                            uploadStatus === 'success' ? 'text-green-600' : 
                            uploadStatus === 'error' ? 'text-red-600' : 'text-gray-700'
                          }`}>
                            {uploadStatus === 'success' ? (
                              <CheckCircle2 className="w-8 h-8" />
                            ) : uploadStatus === 'error' ? (
                              <AlertCircle className="w-8 h-8" />
                            ) : (
                              <FileText className="w-8 h-8 text-violet-600" />
                            )}
                            <div className="text-left">
                              <p className="text-sm">{uploadFile.name}</p>
                              <p className="text-xs text-muted-foreground">
                                {(uploadFile.size / 1024).toFixed(2)} KB
                              </p>
                            </div>
                          </div>
                          
                          <div className="flex gap-2 justify-center">
                            <Button
                              onClick={handleFileUpload}
                              className="bg-gradient-to-r from-violet-600 to-purple-600 hover:from-violet-700 hover:to-purple-700 text-white"
                              disabled={uploadStatus === 'success'}
                            >
                              {uploadStatus === 'success' ? (
                                <>
                                  <CheckCircle2 className="w-4 h-4 mr-2" />
                                  Đã upload
                                </>
                              ) : (
                                <>
                                  <Upload className="w-4 h-4 mr-2" />
                                  Upload ngay
                                </>
                              )}
                            </Button>
                            <Button
                              onClick={clearUpload}
                              variant="outline"
                              className="hover:bg-red-50 hover:text-red-600"
                            >
                              <Trash2 className="w-4 h-4 mr-2" />
                              Xóa
                            </Button>
                          </div>
                        </div>
                      )}
                      
                      {uploadStatus === 'uploading' && (
                        <div className="space-y-4">
                          <Loader2 className="w-16 h-16 mx-auto text-blue-500 animate-spin" />
                          <div>
                            <p className="text-sm mb-2">Đang xử lý file...</p>
                            <Progress value={uploadProgress} className="h-2" />
                            <p className="text-xs text-muted-foreground mt-2">{uploadProgress}%</p>
                          </div>
                        </div>
                      )}
                    </div>
                    
                    {/* Status Messages */}
                    {uploadStatus === 'success' && (
                      <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded-lg text-green-700">
                        <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                        <div className="text-sm">
                          <p>Upload thành công!</p>
                          <p className="text-xs text-green-600">File đã được xử lý và lưu vào hệ thống</p>
                        </div>
                      </div>
                    )}
                    
                    {uploadStatus === 'error' && (
                      <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
                        <AlertCircle className="w-5 h-5 flex-shrink-0" />
                        <div className="text-sm">
                          <p>Upload thất bại!</p>
                          <p className="text-xs text-red-600">Vui lòng kiểm tra file và thử lại</p>
                        </div>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : activeMenu === 'reports' ? (
            /* Reports Section */
            <div className="space-y-6">
              {/* Reports Header */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b bg-gradient-to-r from-orange-50 to-amber-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-gradient-to-br from-orange-600 to-amber-600 rounded-lg flex items-center justify-center">
                          <BarChart3 className="w-5 h-5 text-white" />
                        </div>
                        Báo cáo & Phân tích
                      </CardTitle>
                      <CardDescription>Thống kê và phân tích dữ liệu hệ thống</CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button variant="outline">
                        <FileText className="w-4 h-4 mr-2" />
                        Export PDF
                      </Button>
                      <Button className="bg-gradient-to-r from-orange-600 to-amber-600 hover:from-orange-700 hover:to-amber-700 text-white">
                        <Upload className="w-4 h-4 mr-2" />
                        Export Excel
                      </Button>
                    </div>
                  </div>
                </CardHeader>
              </Card>

              {/* Date Range Filter */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardContent className="p-4">
                  <div className="flex items-center gap-4">
                    <div className="flex items-center gap-2">
                      <Calendar className="w-4 h-4 text-gray-500" />
                      <span className="text-sm">Khoảng thời gian:</span>
                    </div>
                    <select className="px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500">
                      <option>7 ngày qua</option>
                      <option>30 ngày qua</option>
                      <option>3 tháng qua</option>
                      <option>1 năm qua</option>
                      <option>Tùy chỉnh</option>
                    </select>
                  </div>
                </CardContent>
              </Card>

              {/* Charts Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                  <CardHeader className="border-b">
                    <CardTitle className="text-lg">Doanh thu theo tháng</CardTitle>
                  </CardHeader>
                  <CardContent className="p-6">
                    <ResponsiveContainer width="100%" height={300}>
                      <AreaChart data={[
                        { month: 'T1', revenue: 4000000 },
                        { month: 'T2', revenue: 3000000 },
                        { month: 'T3', revenue: 5000000 },
                        { month: 'T4', revenue: 7000000 },
                        { month: 'T5', revenue: 6000000 },
                        { month: 'T6', revenue: 8000000 },
                      ]}>
                        <defs>
                          <linearGradient id="revenueGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#f97316" stopOpacity={0.8}/>
                            <stop offset="95%" stopColor="#f97316" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Area type="monotone" dataKey="revenue" stroke="#f97316" fillOpacity={1} fill="url(#revenueGradient)" />
                      </AreaChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                  <CardHeader className="border-b">
                    <CardTitle className="text-lg">Phân loại hóa đơn</CardTitle>
                  </CardHeader>
                  <CardContent className="p-6">
                    <ResponsiveContainer width="100%" height={300}>
                      <PieChart>
                        <Pie
                          data={[
                            { name: 'Đã thanh toán', value: 845 },
                            { name: 'Chờ xử lý', value: 123 },
                            { name: 'Quá hạn', value: 28 },
                          ]}
                          cx="50%"
                          cy="50%"
                          labelLine={false}
                          label
                          outerRadius={80}
                          fill="#8884d8"
                          dataKey="value"
                        >
                          <Cell fill="#10b981" />
                          <Cell fill="#f59e0b" />
                          <Cell fill="#ef4444" />
                        </Pie>
                        <Tooltip />
                        <Legend />
                      </PieChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </div>
            </div>
          ) : activeMenu === 'files' ? (
            /* Files Management */
            <div className="space-y-6">
              {/* Files Header */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b bg-gradient-to-r from-indigo-50 to-blue-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-lg flex items-center justify-center">
                          <FolderOpen className="w-5 h-5 text-white" />
                        </div>
                        Quản lý tệp tin
                      </CardTitle>
                      <CardDescription>Quản lý các file và tài liệu đã upload</CardDescription>
                    </div>
                    <Button className="bg-gradient-to-r from-indigo-600 to-blue-600 hover:from-indigo-700 hover:to-blue-700 text-white shadow-lg">
                      <Upload className="w-4 h-4 mr-2" />
                      Upload file
                    </Button>
                  </div>
                </CardHeader>
              </Card>

              {/* Storage Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <Card className="bg-gradient-to-br from-indigo-50 to-blue-50 border-indigo-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Tổng files</p>
                        <p className="text-2xl">1,456</p>
                      </div>
                      <FileText className="w-8 h-8 text-indigo-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Dung lượng</p>
                        <p className="text-2xl">24.5GB</p>
                      </div>
                      <Activity className="w-8 h-8 text-purple-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">PDF</p>
                        <p className="text-2xl">845</p>
                      </div>
                      <FileText className="w-8 h-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Images</p>
                        <p className="text-2xl">423</p>
                      </div>
                      <FileText className="w-8 h-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Files Grid */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b">
                  <div className="flex items-center justify-between">
                    <CardTitle>Tệp tin gần đây</CardTitle>
                    <div className="flex gap-2">
                      <Button variant="outline" size="sm">Grid</Button>
                      <Button variant="outline" size="sm">List</Button>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="p-6">
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    {['Invoice_2024.pdf', 'Report_Q4.xlsx', 'Contract_ABC.docx', 'Photo_001.jpg', 'Data_Export.csv', 'Proposal.pdf', 'Budget.xlsx', 'Meeting.docx'].map((file, idx) => (
                      <Card key={idx} className="hover:shadow-lg transition-shadow cursor-pointer group">
                        <CardContent className="p-4 text-center">
                          <div className="w-16 h-16 mx-auto mb-3 bg-gradient-to-br from-indigo-100 to-blue-100 rounded-lg flex items-center justify-center">
                            <FileText className="w-8 h-8 text-indigo-600" />
                          </div>
                          <p className="text-sm truncate">{file}</p>
                          <p className="text-xs text-muted-foreground mt-1">
                            {(Math.random() * 5 + 1).toFixed(1)} MB
                          </p>
                          <div className="flex gap-1 mt-3 opacity-0 group-hover:opacity-100 transition-opacity justify-center">
                            <Button variant="ghost" size="sm">
                              <Eye className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm">
                              <Upload className="w-4 h-4" />
                            </Button>
                            <Button variant="ghost" size="sm" className="hover:bg-red-50">
                              <Trash2 className="w-4 h-4 text-red-600" />
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : activeMenu === 'security' ? (
            /* Security Section */
            <div className="space-y-6">
              {/* Security Header */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b bg-gradient-to-r from-red-50 to-rose-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-rose-600 rounded-lg flex items-center justify-center">
                          <Shield className="w-5 h-5 text-white" />
                        </div>
                        Bảo mật & Quyền truy cập
                      </CardTitle>
                      <CardDescription>Quản lý bảo mật hệ thống và logs hoạt động</CardDescription>
                    </div>
                  </div>
                </CardHeader>
              </Card>

              {/* Security Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <Card className="bg-gradient-to-br from-green-50 to-emerald-50 border-green-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Login thành công</p>
                        <p className="text-2xl">2,345</p>
                      </div>
                      <CheckCircle2 className="w-8 h-8 text-green-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-red-50 to-rose-50 border-red-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Login thất bại</p>
                        <p className="text-2xl">23</p>
                      </div>
                      <AlertCircle className="w-8 h-8 text-red-600" />
                    </div>
                  </CardContent>
                </Card>
                <Card className="bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
                  <CardContent className="p-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-muted-foreground">Phiên hoạt động</p>
                        <p className="text-2xl">156</p>
                      </div>
                      <Activity className="w-8 h-8 text-blue-600" />
                    </div>
                  </CardContent>
                </Card>
              </div>

              {/* Activity Logs */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b">
                  <CardTitle>Logs hoạt động gần đây</CardTitle>
                </CardHeader>
                <CardContent className="p-0">
                  <div className="divide-y divide-gray-200">
                    {[
                      { action: 'User login', user: 'admin@invoice.com', time: '2 phút trước', type: 'success' },
                      { action: 'File uploaded', user: 'user@invoice.com', time: '15 phút trước', type: 'info' },
                      { action: 'Failed login attempt', user: 'unknown@example.com', time: '1 giờ trước', type: 'error' },
                      { action: 'Password changed', user: 'user@invoice.com', time: '2 giờ trước', type: 'warning' },
                      { action: 'New user created', user: 'admin@invoice.com', time: '3 giờ trước', type: 'success' },
                    ].map((log, idx) => (
                      <div key={idx} className="p-4 hover:bg-gray-50 transition-colors">
                        <div className="flex items-start gap-4">
                          <div className={`w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0 ${
                            log.type === 'success' ? 'bg-green-100' :
                            log.type === 'error' ? 'bg-red-100' :
                            log.type === 'warning' ? 'bg-yellow-100' :
                            'bg-blue-100'
                          }`}>
                            {log.type === 'success' ? <CheckCircle2 className="w-5 h-5 text-green-600" /> :
                             log.type === 'error' ? <AlertCircle className="w-5 h-5 text-red-600" /> :
                             log.type === 'warning' ? <AlertCircle className="w-5 h-5 text-yellow-600" /> :
                             <Activity className="w-5 h-5 text-blue-600" />}
                          </div>
                          <div className="flex-1">
                            <p className="text-sm">{log.action}</p>
                            <p className="text-xs text-muted-foreground">{log.user}</p>
                          </div>
                          <div className="text-xs text-muted-foreground flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {log.time}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : activeMenu === 'settings' ? (
            /* Settings Section */
            <div className="space-y-6">
              {/* Settings Header */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                <CardHeader className="border-b bg-gradient-to-r from-slate-50 to-gray-50">
                  <div className="flex items-center justify-between">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        <div className="w-10 h-10 bg-gradient-to-br from-slate-600 to-gray-600 rounded-lg flex items-center justify-center">
                          <Settings className="w-5 h-5 text-white" />
                        </div>
                        Cài đặt hệ thống
                      </CardTitle>
                      <CardDescription>Cấu hình và tùy chỉnh hệ thống</CardDescription>
                    </div>
                    <Button className="bg-gradient-to-r from-slate-600 to-gray-600 hover:from-slate-700 hover:to-gray-700 text-white shadow-lg">
                      <Save className="w-4 h-4 mr-2" />
                      Lưu thay đổi
                    </Button>
                  </div>
                </CardHeader>
              </Card>

              {/* Settings Grid */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* General Settings */}
                <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                  <CardHeader className="border-b">
                    <CardTitle className="text-lg">Cài đặt chung</CardTitle>
                  </CardHeader>
                  <CardContent className="p-6 space-y-4">
                    <div>
                      <label className="text-sm mb-2 block">Tên hệ thống</label>
                      <input
                        type="text"
                        defaultValue="Invoice Management System"
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                      />
                    </div>
                    <div>
                      <label className="text-sm mb-2 block">Email hệ thống</label>
                      <input
                        type="email"
                        defaultValue="system@invoice.com"
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                      />
                    </div>
                    <div>
                      <label className="text-sm mb-2 block">Múi giờ</label>
                      <select className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500">
                        <option>Asia/Ho_Chi_Minh (UTC+7)</option>
                        <option>Asia/Bangkok (UTC+7)</option>
                        <option>Asia/Singapore (UTC+8)</option>
                      </select>
                    </div>
                  </CardContent>
                </Card>

                {/* Email Settings */}
                <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                  <CardHeader className="border-b">
                    <CardTitle className="text-lg">Cài đặt Email</CardTitle>
                  </CardHeader>
                  <CardContent className="p-6 space-y-4">
                    <div>
                      <label className="text-sm mb-2 block">SMTP Server</label>
                      <input
                        type="text"
                        defaultValue="smtp.gmail.com"
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                      />
                    </div>
                    <div>
                      <label className="text-sm mb-2 block">SMTP Port</label>
                      <input
                        type="text"
                        defaultValue="587"
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                      />
                    </div>
                    <div>
                      <label className="text-sm mb-2 block">SMTP Username</label>
                      <input
                        type="email"
                        placeholder="your-email@gmail.com"
                        className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-slate-500"
                      />
                    </div>
                  </CardContent>
                </Card>

                {/* Backup Settings */}
                <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                  <CardHeader className="border-b">
                    <CardTitle className="text-lg">Sao lưu & Phục hồi</CardTitle>
                  </CardHeader>
                  <CardContent className="p-6 space-y-4">
                    <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg">
                      <div>
                        <p className="text-sm">Sao lưu tự động</p>
                        <p className="text-xs text-muted-foreground">Lần cuối: 24/11/2024</p>
                      </div>
                      <Button size="sm" className="bg-blue-600 hover:bg-blue-700 text-white">
                        Sao lưu ngay
                      </Button>
                    </div>
                    <div className="flex items-center justify-between p-4 bg-green-50 rounded-lg">
                      <div>
                        <p className="text-sm">Phục hồi dữ liệu</p>
                        <p className="text-xs text-muted-foreground">Từ bản sao lưu</p>
                      </div>
                      <Button size="sm" variant="outline">
                        Phục hồi
                      </Button>
                    </div>
                  </CardContent>
                </Card>

                {/* Notifications Settings */}
                <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg">
                  <CardHeader className="border-b">
                    <CardTitle className="text-lg">Thông báo</CardTitle>
                  </CardHeader>
                  <CardContent className="p-6 space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm">Email notifications</p>
                        <p className="text-xs text-muted-foreground">Nhận thông báo qua email</p>
                      </div>
                      <input type="checkbox" defaultChecked className="w-5 h-5" />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm">Push notifications</p>
                        <p className="text-xs text-muted-foreground">Thông báo trên trình duyệt</p>
                      </div>
                      <input type="checkbox" defaultChecked className="w-5 h-5" />
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm">SMS notifications</p>
                        <p className="text-xs text-muted-foreground">Nhận thông báo qua SMS</p>
                      </div>
                      <input type="checkbox" className="w-5 h-5" />
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          ) : (
            /* Dashboard Content */
            <>
          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm">Tổng người dùng</CardTitle>
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-600 rounded-xl flex items-center justify-center shadow-md">
                  <Users className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl mb-1">1,234</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">↑ +12%</span> so với tháng trước
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm">Tổng hóa đơn</CardTitle>
                <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center shadow-md">
                  <FileText className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl mb-1">45,231</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">↑ +20%</span> so với tháng trước
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm">Doanh thu</CardTitle>
                <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-md">
                  <DollarSign className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl mb-1">$12,345</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">↑ +18%</span> so với tháng trước
                </p>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <CardTitle className="text-sm">Hoạt động</CardTitle>
                <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-600 rounded-xl flex items-center justify-center shadow-md">
                  <Activity className="h-5 w-5 text-white" />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-3xl mb-1">573</div>
                <p className="text-xs text-muted-foreground">
                  <span className="text-green-600">↑ +7%</span> so với tuần trước
                </p>
              </CardContent>
            </Card>
          </div>

          {/* Recent Activity */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-cyan-50">
                <CardTitle className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-lg flex items-center justify-center">
                    <Activity className="w-4 h-4 text-white" />
                  </div>
                  Hoạt động gần đây
                </CardTitle>
                <CardDescription>Các hoạt động mới nhất trong hệ thống</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-4">
                  {[
                    { user: 'Nguyễn Văn A', action: 'Tạo hóa đơn mới', time: '5 phút trước' },
                    { user: 'Trần Thị B', action: 'Cập nhật thông tin', time: '15 phút trước' },
                    { user: 'Lê Văn C', action: 'Thanh toán hóa đơn', time: '30 phút trước' },
                    { user: 'Phạm Thị D', action: 'Đăng ký tài khoản', time: '1 giờ trước' },
                  ].map((activity, idx) => (
                    <div key={idx} className="flex items-center justify-between pb-3 border-b last:border-0">
                      <div>
                        <p className="text-sm">{activity.user}</p>
                        <p className="text-xs text-muted-foreground">{activity.action}</p>
                      </div>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="border-b bg-gradient-to-r from-purple-50 to-pink-50">
                <CardTitle className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                    <Users className="w-4 h-4 text-white" />
                  </div>
                  Người dùng hoạt động
                </CardTitle>
                <CardDescription>Top người dùng tích cực nhất</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <div className="space-y-4">
                  {[
                    { name: 'Nguyễn Văn A', invoices: 45, email: 'user1@example.com' },
                    { name: 'Trần Thị B', invoices: 38, email: 'user2@example.com' },
                    { name: 'Lê Văn C', invoices: 32, email: 'user3@example.com' },
                    { name: 'Phạm Thị D', invoices: 28, email: 'user4@example.com' },
                  ].map((user, idx) => (
                    <div key={idx} className="flex items-center justify-between pb-3 border-b last:border-0">
                      <div className="flex items-center gap-3">
                        <Avatar className="w-8 h-8 border-2 border-purple-100">
                          <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white text-xs">
                            {user.name.charAt(0)}
                          </AvatarFallback>
                        </Avatar>
                        <div>
                          <p className="text-sm">{user.name}</p>
                          <p className="text-xs text-muted-foreground">{user.email}</p>
                        </div>
                      </div>
                      <Badge variant="secondary" className="bg-purple-100 text-purple-700">{user.invoices} hóa đơn</Badge>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-cyan-50">
                <CardTitle className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-lg flex items-center justify-center">
                    <BarChart3 className="w-4 h-4 text-white" />
                  </div>
                  Doanh thu hàng tháng
                </CardTitle>
                <CardDescription>Doanh thu và số hóa đơn hàng tháng</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={revenueData}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="revenue" stroke="#8884d8" activeDot={{ r: 8 }} />
                    <Line type="monotone" dataKey="invoices" stroke="#82ca9d" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="border-b bg-gradient-to-r from-purple-50 to-pink-50">
                <CardTitle className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                    <Users className="w-4 h-4 text-white" />
                  </div>
                  Tăng trưởng người dùng
                </CardTitle>
                <CardDescription>Số lượng người dùng hàng tháng</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart
                    data={userGrowthData}
                    margin={{
                      top: 5,
                      right: 30,
                      left: 20,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="users" stroke="#8884d8" activeDot={{ r: 8 }} />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Pie Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-cyan-50">
                <CardTitle className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-cyan-600 rounded-lg flex items-center justify-center">
                    <PieChart className="w-4 h-4 text-white" />
                  </div>
                  Phân loại hóa đơn
                </CardTitle>
                <CardDescription>Phân loại hóa đơn theo danh mục</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={categoryData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                    >
                      {categoryData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="border-b bg-gradient-to-r from-purple-50 to-pink-50">
                <CardTitle className="flex items-center gap-2">
                  <div className="w-8 h-8 bg-gradient-to-br from-purple-600 to-pink-600 rounded-lg flex items-center justify-center">
                    <PieChart className="w-4 h-4 text-white" />
                  </div>
                  Trạng thái công việc
                </CardTitle>
                <CardDescription>Trạng thái công việc hiện tại</CardDescription>
              </CardHeader>
              <CardContent className="p-6">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={taskData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                    >
                      {taskData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>
        </>
          )}
        </main>
      </div>
    </div>
  );
}
