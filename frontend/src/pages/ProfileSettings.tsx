import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import { 
  ArrowLeft, 
  User, 
  Mail, 
  Lock, 
  Camera,
  Save,
  Shield,
  Bell,
  Eye,
  EyeOff
} from 'lucide-react';
import { Switch } from '@/components/ui/switch';

interface ProfileSettingsProps {
  user: {
    email: string;
    name: string;
  };
  onBack: () => void;
  onUpdate: (name: string, email: string) => void;
}

export function ProfileSettings({ user, onBack, onUpdate }: ProfileSettingsProps) {
  const [name, setName] = useState(user.name);
  const [email, setEmail] = useState(user.email);
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showCurrentPassword, setShowCurrentPassword] = useState(false);
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [pushNotifications, setPushNotifications] = useState(true);
  const [saveSuccess, setSaveSuccess] = useState(false);

  const handleSaveProfile = () => {
    onUpdate(name, email);
    setSaveSuccess(true);
    setTimeout(() => setSaveSuccess(false), 3000);
  };

  const handleChangePassword = () => {
    if (newPassword !== confirmPassword) {
      alert('Mật khẩu xác nhận không khớp!');
      return;
    }
    if (newPassword.length < 6) {
      alert('Mật khẩu phải có ít nhất 6 ký tự!');
      return;
    }
    alert('Đổi mật khẩu thành công!');
    setCurrentPassword('');
    setNewPassword('');
    setConfirmPassword('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={onBack}
              className="hover:bg-white/50 rounded-xl"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-3xl bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Cài đặt tài khoản
              </h1>
              <p className="text-muted-foreground">Quản lý thông tin cá nhân và cài đặt bảo mật</p>
            </div>
          </div>
          
          {/* Success Message - Floating */}
          {saveSuccess && (
            <div className="bg-green-50 border border-green-200 rounded-xl p-3 flex items-center gap-3 animate-in slide-in-from-right duration-300 shadow-lg">
              <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <p className="text-green-800">Đã lưu thành công!</p>
            </div>
          )}
        </div>

        {/* Main Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Profile Card (Spans 1 column) */}
          <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 lg:col-span-1 flex flex-col">
            <CardHeader className="border-b bg-gradient-to-r from-blue-50 to-purple-50">
              <CardTitle className="flex items-center gap-2 text-lg">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-md">
                  <User className="w-5 h-5 text-white" />
                </div>
                Thông tin cá nhân
              </CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-5 flex-1">
              {/* Avatar Section - Centered */}
              <div className="flex flex-col items-center text-center pt-2">
                <div className="relative group mb-4">
                  <Avatar className="w-28 h-28 border-4 border-white shadow-xl">
                    <AvatarImage src="" />
                    <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-500 text-white text-3xl">
                      {name.charAt(0).toUpperCase()}
                    </AvatarFallback>
                  </Avatar>
                  <div className="absolute inset-0 bg-black/40 rounded-full opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center cursor-pointer">
                    <Camera className="w-7 h-7 text-white" />
                  </div>
                </div>
                <h3 className="text-lg mb-1">{name}</h3>
                <p className="text-sm text-muted-foreground mb-3">{email}</p>
                <Button size="sm" variant="outline" className="rounded-xl h-9 px-4">
                  <Camera className="w-4 h-4 mr-2" />
                  Đổi ảnh
                </Button>
              </div>

              <Separator />

              {/* Name Field */}
              <div className="space-y-2">
                <Label htmlFor="name" className="flex items-center gap-2 text-sm">
                  <User className="w-4 h-4 text-blue-600" />
                  Họ và tên
                </Label>
                <Input
                  id="name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="h-11 rounded-xl"
                  placeholder="Nhập họ và tên"
                />
              </div>

              {/* Email Field */}
              <div className="space-y-2">
                <Label htmlFor="email" className="flex items-center gap-2 text-sm">
                  <Mail className="w-4 h-4 text-purple-600" />
                  Email
                </Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="h-11 rounded-xl"
                  placeholder="Nhập email"
                />
              </div>

              {/* Save Button */}
              <Button 
                onClick={handleSaveProfile}
                className="w-full h-12 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 shadow-lg hover:shadow-xl transition-all rounded-xl mt-auto"
              >
                <Save className="w-4 h-4 mr-2" />
                Lưu thay đổi
              </Button>
            </CardContent>
          </Card>

          {/* Right Column - Security & Notifications (Spans 2 columns) */}
          <div className="lg:col-span-2 space-y-6 flex flex-col">
            {/* Security Settings */}
            <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300">
              <CardHeader className="border-b bg-gradient-to-r from-orange-50 to-red-50">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <div className="w-10 h-10 bg-gradient-to-br from-orange-600 to-red-600 rounded-xl flex items-center justify-center shadow-md">
                    <Shield className="w-5 h-5 text-white" />
                  </div>
                  Bảo mật & Mật khẩu
                </CardTitle>
              </CardHeader>
              <CardContent className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  {/* Current Password */}
                  <div className="space-y-2">
                    <Label htmlFor="current-password" className="flex items-center gap-2 text-sm">
                      <Lock className="w-4 h-4 text-orange-600" />
                      Mật khẩu hiện tại
                    </Label>
                    <div className="relative">
                      <Input
                        id="current-password"
                        type={showCurrentPassword ? "text" : "password"}
                        value={currentPassword}
                        onChange={(e) => setCurrentPassword(e.target.value)}
                        className="h-11 pr-10 rounded-xl"
                        placeholder="Nhập mật khẩu"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute right-1 top-1/2 -translate-y-1/2 rounded-lg h-9 w-9"
                        onClick={() => setShowCurrentPassword(!showCurrentPassword)}
                      >
                        {showCurrentPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </Button>
                    </div>
                  </div>

                  {/* New Password */}
                  <div className="space-y-2">
                    <Label htmlFor="new-password" className="flex items-center gap-2 text-sm">
                      <Lock className="w-4 h-4 text-orange-600" />
                      Mật khẩu mới
                    </Label>
                    <div className="relative">
                      <Input
                        id="new-password"
                        type={showNewPassword ? "text" : "password"}
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        className="h-11 pr-10 rounded-xl"
                        placeholder="Nhập mật khẩu mới"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute right-1 top-1/2 -translate-y-1/2 rounded-lg h-9 w-9"
                        onClick={() => setShowNewPassword(!showNewPassword)}
                      >
                        {showNewPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </Button>
                    </div>
                  </div>

                  {/* Confirm Password */}
                  <div className="space-y-2">
                    <Label htmlFor="confirm-password" className="flex items-center gap-2 text-sm">
                      <Lock className="w-4 h-4 text-orange-600" />
                      Xác nhận mật khẩu
                    </Label>
                    <div className="relative">
                      <Input
                        id="confirm-password"
                        type={showConfirmPassword ? "text" : "password"}
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className="h-11 pr-10 rounded-xl"
                        placeholder="Nhập lại mật khẩu"
                      />
                      <Button
                        type="button"
                        variant="ghost"
                        size="icon"
                        className="absolute right-1 top-1/2 -translate-y-1/2 rounded-lg h-9 w-9"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      >
                        {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </Button>
                    </div>
                  </div>
                </div>

                <Button 
                  onClick={handleChangePassword}
                  variant="outline"
                  className="w-full h-12 border-2 hover:bg-orange-50 mt-6 rounded-xl"
                  disabled={!currentPassword || !newPassword || !confirmPassword}
                >
                  <Lock className="w-4 h-4 mr-2" />
                  Đổi mật khẩu
                </Button>
              </CardContent>
            </Card>

            {/* Bottom Row - Notifications & Danger Zone */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 flex-1">
              {/* Notification Settings */}
              <Card className="bg-white/80 backdrop-blur-xl border-gray-200 shadow-lg hover:shadow-xl transition-all duration-300 flex flex-col">
                <CardHeader className="border-b bg-gradient-to-r from-green-50 to-emerald-50">
                  <CardTitle className="flex items-center gap-2 text-lg">
                    <div className="w-10 h-10 bg-gradient-to-br from-green-600 to-emerald-600 rounded-xl flex items-center justify-center shadow-md">
                      <Bell className="w-5 h-5 text-white" />
                    </div>
                    Thông báo
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6 space-y-5 flex-1 flex flex-col justify-center">
                  {/* Email Notifications */}
                  <div className="flex items-center justify-between py-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Mail className="w-4 h-4 text-green-600" />
                        <h4 className="text-sm">Thông báo Email</h4>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Nhận thông báo qua email
                      </p>
                    </div>
                    <Switch
                      checked={emailNotifications}
                      onCheckedChange={setEmailNotifications}
                    />
                  </div>

                  <Separator />

                  {/* Push Notifications */}
                  <div className="flex items-center justify-between py-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Bell className="w-4 h-4 text-green-600" />
                        <h4 className="text-sm">Thông báo đẩy</h4>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        Thông báo trực tiếp trên trình duyệt
                      </p>
                    </div>
                    <Switch
                      checked={pushNotifications}
                      onCheckedChange={setPushNotifications}
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Danger Zone */}
              <Card className="bg-white/80 backdrop-blur-xl border-red-200 shadow-lg hover:shadow-xl transition-all duration-300 flex flex-col">
                <CardHeader className="border-b bg-red-50">
                  <CardTitle className="text-red-600 text-lg flex items-center gap-2">
                    <div className="w-10 h-10 bg-gradient-to-br from-red-600 to-red-700 rounded-xl flex items-center justify-center shadow-md">
                      <Shield className="w-5 h-5 text-white" />
                    </div>
                    Vùng nguy hiểm
                  </CardTitle>
                </CardHeader>
                <CardContent className="p-6 flex flex-col justify-center flex-1">
                  <div className="flex flex-col items-center justify-center h-full space-y-4">
                    <div className="text-center">
                      <p className="text-sm text-muted-foreground mb-1">
                        Xóa vĩnh viễn tài khoản của bạn
                      </p>
                      <p className="text-xs text-muted-foreground">
                        Hành động này không thể hoàn tác
                      </p>
                    </div>
                    <Button 
                      variant="destructive"
                      className="w-full h-12 rounded-xl"
                    >
                      Xóa tài khoản
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
