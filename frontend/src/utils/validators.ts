/**
 * Validate email format
 * @param email - Email to validate
 * @returns true if email is valid
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * Validate password strength
 * @param password - Password to validate
 * @returns Validation result with message
 */
export function validatePassword(password: string): { valid: boolean; message: string } {
  if (password.length < 6) {
    return { valid: false, message: 'Mật khẩu phải có ít nhất 6 ký tự' };
  }
  if (password.length > 50) {
    return { valid: false, message: 'Mật khẩu không được quá 50 ký tự' };
  }
  return { valid: true, message: '' };
}

/**
 * Validate required field
 * @param value - Value to validate
 * @param fieldName - Name of the field
 * @returns Validation result with message
 */
export function validateRequired(value: string, fieldName: string): { valid: boolean; message: string } {
  if (!value || value.trim().length === 0) {
    return { valid: false, message: `${fieldName} là bắt buộc` };
  }
  return { valid: true, message: '' };
}

/**
 * Validate name field
 * @param name - Name to validate
 * @returns Validation result with message
 */
export function validateName(name: string): { valid: boolean; message: string } {
  if (!name || name.trim().length === 0) {
    return { valid: false, message: 'Tên là bắt buộc' };
  }
  if (name.length < 2) {
    return { valid: false, message: 'Tên phải có ít nhất 2 ký tự' };
  }
  if (name.length > 50) {
    return { valid: false, message: 'Tên không được quá 50 ký tự' };
  }
  return { valid: true, message: '' };
}
