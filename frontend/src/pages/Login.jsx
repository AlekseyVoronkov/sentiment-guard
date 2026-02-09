import React, { useState } from 'react';
import { Card, Input, Button, Typography, message, Space, Form } from 'antd';
import { useNavigate, Link } from 'react-router-dom';
import api from '../api';

const { Title } = Typography;

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async () => {
    if (!email || !password) {
        message.warning('Пожалуйста, заполните все поля');
        return;
    }

    setLoading(true);

    try {
      const formData = new URLSearchParams();
      formData.append('username', email);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData);
      
      localStorage.setItem('token', response.data.access_token);
      
      message.success('Вход успешен!');
      navigate('/');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Ошибка входа';
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', background: '#f0f2f5' }}>
      <Card style={{ width: 400, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
            <Title level={2}>Вход</Title>
        </div>
        
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
            <Input 
                size="large" 
                placeholder="Email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
            />
            <Input.Password
                size="large"
                placeholder="Пароль" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
            />
            <Button type="primary" size="large" onClick={handleLogin} loading={loading} block>
                Войти
            </Button>
            <div style={{ textAlign: 'center' }}>
                Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
            </div>
        </Space>
      </Card>
    </div>
  );
};

export default Login;