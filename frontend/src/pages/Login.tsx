import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUser, FiLock, FiMail, FiArrowRight } from 'react-icons/fi';
import { authAPI } from '../services/api';

const Login: React.FC = () => {
  const navigate = useNavigate();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (isLogin) {
        const response = await authAPI.login({
          username: formData.username,
          password: formData.password
        });

        if (response.data.token) {
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('user', JSON.stringify(response.data.user));
          navigate('/');
        }
      } else {
        if (formData.password !== formData.confirmPassword) {
          setError('Пароли не совпадают');
          setLoading(false);
          return;
        }

        const response = await authAPI.register({
          username: formData.username,
          email: formData.email,
          password: formData.password,
          password2: formData.confirmPassword
        });

        if (response.data.token) {
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('user', JSON.stringify(response.data.user));
          navigate('/');
        }
      }
    } catch (err: any) {
      console.error('Auth error:', err.response?.data);
      // Обработка разных форматов ошибок от сервера
      const errorData = err.response?.data;
      if (typeof errorData === 'string') {
        setError(errorData);
      } else if (errorData?.message) {
        setError(errorData.message);
      } else if (errorData?.detail) {
        setError(errorData.detail);
      } else if (errorData?.non_field_errors) {
        setError(errorData.non_field_errors.join(', '));
      } else if (errorData?.username) {
        setError(`Логин: ${errorData.username.join(', ')}`);
      } else if (errorData?.email) {
        setError(`Email: ${errorData.email.join(', ')}`);
      } else if (errorData?.password) {
        setError(`Пароль: ${errorData.password.join(', ')}`);
      } else {
        setError('Ошибка авторизации. Попробуйте снова.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4">
      <div className="w-full max-w-md">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 bg-primary mb-6">
            {React.createElement(FiUser as any, { className: "text-2xl text-white" })}
          </div>
          <h1 className="text-heading text-2xl md:text-3xl text-white mb-2">
            {isLogin ? 'Вход в аккаунт' : 'Создание аккаунта'}
          </h1>
          <p className="text-gray-500">
            {isLogin 
              ? 'Введите данные для входа' 
              : 'Заполните форму для регистрации'}
          </p>
        </div>

        {/* Form Card */}
        <div className="card p-8">
          <form onSubmit={handleSubmit} className="space-y-5">
            {/* Username */}
            <div>
              <label className="label">Имя пользователя</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  {React.createElement(FiUser as any, { className: "text-gray-500" })}
                </div>
                <input
                  type="text"
                  name="username"
                  value={formData.username}
                  onChange={handleChange}
                  className="input pl-11"
                  placeholder="Введите логин"
                  required
                />
              </div>
            </div>

            {/* Email (only for registration) */}
            {!isLogin && (
              <div>
                <label className="label">Email</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    {React.createElement(FiMail as any, { className: "text-gray-500" })}
                  </div>
                  <input
                    type="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    className="input pl-11"
                    placeholder="your@email.com"
                    required
                  />
                </div>
              </div>
            )}

            {/* Password */}
            <div>
              <label className="label">Пароль</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                  {React.createElement(FiLock as any, { className: "text-gray-500" })}
                </div>
                <input
                  type="password"
                  name="password"
                  value={formData.password}
                  onChange={handleChange}
                  className="input pl-11"
                  placeholder="••••••••"
                  required
                />
              </div>
            </div>

            {/* Confirm Password (only for registration) */}
            {!isLogin && (
              <div>
                <label className="label">Подтвердите пароль</label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                    {React.createElement(FiLock as any, { className: "text-gray-500" })}
                  </div>
                  <input
                    type="password"
                    name="confirmPassword"
                    value={formData.confirmPassword}
                    onChange={handleChange}
                    className="input pl-11"
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>
            )}

            {/* Error */}
            {error && (
              <div className="p-4 bg-red-500/10 border border-red-500/30 text-red-400 text-sm">
                {error}
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3"
            >
              {loading ? (
                <div className="spinner w-5 h-5 border-2" />
              ) : (
                <>
                  <span>{isLogin ? 'Войти' : 'Создать аккаунт'}</span>
                  {React.createElement(FiArrowRight as any, {})}
                </>
              )}
            </button>
          </form>

          {/* Toggle */}
          <div className="mt-6 pt-6 border-t border-border-dark text-center">
            <p className="text-gray-500 text-sm">
              {isLogin ? 'Нет аккаунта?' : 'Уже есть аккаунт?'}
            </p>
            <button
              onClick={() => {
                setIsLogin(!isLogin);
                setError('');
              }}
              className="mt-2 text-primary hover:text-primary-light transition-colors duration-200 text-sm font-medium"
            >
              {isLogin ? 'Создать аккаунт' : 'Войти'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
