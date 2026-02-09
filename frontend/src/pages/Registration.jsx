import React, { useState } from 'react';
import { Card, Input, Button, Typography, message, Space } from 'antd';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const { Title, Text } = Typography;

const Registration = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const handleRegistration = async () => {
    if (!email || !password) {
        message.warning('Пожалуйста, заполните все поля');
        return;
    }

    setLoading(true);

    try {
      await api.post('/auth/register/', { email, password });
      message.success('Регистрация успешна! Теперь вы можете войти.');
      navigate('/login');
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Что-то пошло не так';
      message.error(`Ошибка: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      height: '100vh', 
      background: '#f0f2f5'
    }}>
      <Card style={{ width: 600, boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}>
        <div style={{ textAlign: 'center', marginBottom: 20 }}>
            <Title level={2} style={{ marginBottom: 0 }}>Регистрация</Title>
        </div>
        
        <Space orientation="vertical" size="large" style={{ width: '100%' }}>
                <div style={{ display: 'flex', gap: 10, marginTop: 5 }}>
                    <Input 
                        size="large" 
                        placeholder="Введите свой email" 
                        value={email} 
                        onChange={(e) => setEmail(e.target.value)} 
                    />
                </div>
                <div>
                    <Input.Password
                        visibilityToggle 
                        size="large"
                        placeholder="Введите пароль" 
                        value={password} 
                        onChange={(e) => setPassword(e.target.value)} 
                    />
                </div>
                <div style={{display: 'flex', justifyContent: 'flex-end'}}>
                    <Button 
                        type="primary" 
                        size="large" 
                        onClick={handleRegistration} 
                        loading={loading}
                    >
                        Зарегистрироваться
                    </Button>
                </div>
        </Space>
      </Card>
    </div>
  );
};

export default Registration;