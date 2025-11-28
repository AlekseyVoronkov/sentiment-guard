import React, { useState } from 'react';
import { Card, Input, Button, Typography, message, Space } from 'antd';
import { useNavigate } from 'react-router-dom';
import api from '../api';

const { Title, Text } = Typography;

const Home = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (!url) {
        message.warning('Пожалуйста, введите ссылку');
        return;
    }

    setLoading(true);
    try {
      const res = await api.post('/companies/', {
        name: "Моя Компания", 
        url: url
      });
      
      message.success('Компания найдена!');
      
      navigate(`/company/${res.data.id}`);
      
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Что-то пошло не так';
      message.error(`Ошибка: ${errorMsg}`);
    } finally {
      setLoading(false);
    }
  };

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
            <Title level={2} style={{ marginBottom: 0 }}>Sentiment Guard</Title>
            <Text type="secondary">Система мониторинга репутации</Text>
        </div>
        
        <Space orientation="vertical" size="large" style={{ width: '100%' }}>
            <div>
                <Text strong>Введите ссылку на отзывы (Яндекс.Карты):</Text>
                <div style={{ display: 'flex', gap: 10, marginTop: 5 }}>
                <Input 
                    size="large" 
                    placeholder="https://yandex.ru/maps/org/..." 
                    value={url} 
                    onChange={(e) => setUrl(e.target.value)} 
                    onPressEnter={handleAnalyze}
                />
                <Button 
                    type="primary" 
                    size="large" 
                    onClick={handleAnalyze} 
                    loading={loading}
                >
                    Анализ
                </Button>
                </div>
            </div>
            
            <div style={{ background: '#fafafa', padding: 15, borderRadius: 8 }}>
                <Text type="secondary" style={{ fontSize: 12 }}>
                    Подсказка: Зайдите на Яндекс.Карты, откройте карточку организации, перейдите во вкладку "Отзывы" и скопируйте ссылку из адресной строки.
                </Text>
            </div>
        </Space>
      </Card>
    </div>
  );
};

export default Home;