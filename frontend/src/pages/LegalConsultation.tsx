import React, { useState, useRef, useEffect } from 'react';
import {
  Card,
  Input,
  Button,
  List,
  Avatar,
  Typography,
  Space,
  Tag,
  Select,
  message,
  Spin,
  Divider,
  Tooltip,
  Progress,
  Row,
  Col,
} from 'antd';
import {
  SendOutlined,
  RobotOutlined,
  UserOutlined,
  MessageOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { legalAIAPI } from '../services/api';
import ReactMarkdown from 'react-markdown';

const { TextArea } = Input;
const { Title, Text } = Typography;
const { Option } = Select;

interface Message {
  id: string;
  type: 'user' | 'ai';
  content: string;
  timestamp: Date;
  confidence?: number;
  category?: string;
  sources?: string[];
}

const LegalConsultation: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const queryClient = useQueryClient();

  // 获取法律分类
  const { data: categories } = useQuery('legal-categories', legalAIAPI.getCategories);

  // 获取历史咨询记录
  const { data: consultationHistory } = useQuery(
    'consultation-history',
    () => legalAIAPI.getConsultations(0, 20)
  );

  // 发送咨询的mutation
  const consultMutation = useMutation(legalAIAPI.consult, {
    onSuccess: (response) => {
      const aiMessage: Message = {
        id: Date.now().toString(),
        type: 'ai',
        content: response.data.answer,
        timestamp: new Date(),
        confidence: response.data.confidence,
        category: response.data.category,
        sources: response.data.sources,
      };
      setMessages(prev => [...prev, aiMessage]);
      setIsLoading(false);
      queryClient.invalidateQueries('consultation-history');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '咨询失败，请重试');
      setIsLoading(false);
    },
  });

  // 自动滚动到底部
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) {
      message.warning('请输入您的问题');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      await consultMutation.mutateAsync(inputValue);
    } catch (error) {
      console.error('咨询失败:', error);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'green';
    if (confidence >= 0.6) return 'orange';
    return 'red';
  };

  const getConfidenceText = (confidence: number) => {
    if (confidence >= 0.8) return '高';
    if (confidence >= 0.6) return '中';
    return '低';
  };

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>
        智能法律咨询
      </Title>

      <Row gutter={[16, 16]}>
        {/* 咨询界面 */}
        <Col xs={24} lg={16}>
          <Card className="consultation-chat">
            {/* 聊天消息区域 */}
            <div className="chat-messages">
              {messages.length === 0 ? (
                <div className="empty-state">
                  <RobotOutlined className="empty-state-icon" />
                  <Title level={4} type="secondary">
                    欢迎使用AI法律咨询服务
                  </Title>
                  <Text type="secondary">
                    基于DeepSeek R1和BERT模型，为您提供专业的法律咨询和建议
                  </Text>
                </div>
              ) : (
                messages.map((message) => (
                  <div
                    key={message.id}
                    className={`message message-${message.type}`}
                  >
                    <div className="message-content">
                      <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                        <Avatar
                          icon={message.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
                          style={{
                            backgroundColor: message.type === 'user' ? '#1890ff' : '#52c41a',
                            flexShrink: 0,
                          }}
                        />
                        <div style={{ flex: 1 }}>
                          <div style={{ marginBottom: '4px' }}>
                            <Text strong>
                              {message.type === 'user' ? '您' : 'AI法律助手'}
                            </Text>
                            <Text type="secondary" style={{ marginLeft: '8px', fontSize: '12px' }}>
                              {message.timestamp.toLocaleTimeString()}
                            </Text>
                          </div>
                          <div>
                            {message.type === 'ai' ? (
                              <ReactMarkdown>{message.content}</ReactMarkdown>
                            ) : (
                              <Text>{message.content}</Text>
                            )}
                          </div>
                          {message.type === 'ai' && message.confidence && (
                            <div style={{ marginTop: '8px' }}>
                              <Space>
                                <Tag color={getConfidenceColor(message.confidence)}>
                                  置信度: {getConfidenceText(message.confidence)} ({Math.round(message.confidence * 100)}%)
                                </Tag>
                                {message.category && (
                                  <Tag color="blue">
                                    分类: {message.category}
                                  </Tag>
                                )}
                              </Space>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))
              )}
              
              {isLoading && (
                <div className="message message-ai">
                  <div className="message-content">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <Avatar icon={<RobotOutlined />} style={{ backgroundColor: '#52c41a' }} />
                      <div>
                        <Text>AI正在思考中...</Text>
                        <Spin size="small" style={{ marginLeft: '8px' }} />
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* 输入区域 */}
            <div className="chat-input">
              <div style={{ marginBottom: '12px' }}>
                <Select
                  placeholder="选择法律领域（可选）"
                  style={{ width: '100%' }}
                  value={selectedCategory}
                  onChange={setSelectedCategory}
                  allowClear
                >
                  {categories?.data?.categories?.map((category: any) => (
                    <Option key={category.id} value={category.id}>
                      {category.name}
                    </Option>
                  ))}
                </Select>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <TextArea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="请输入您的法律问题..."
                  autoSize={{ minRows: 2, maxRows: 4 }}
                  style={{ flex: 1 }}
                />
                <Button
                  type="primary"
                  icon={<SendOutlined />}
                  onClick={handleSendMessage}
                  loading={isLoading}
                  disabled={!inputValue.trim()}
                  style={{ height: 'auto' }}
                >
                  发送
                </Button>
              </div>
            </div>
          </Card>
        </Col>

        {/* 侧边栏 */}
        <Col xs={24} lg={8}>
          {/* 历史记录 */}
          <Card title="最近咨询" size="small" style={{ marginBottom: '16px' }}>
            <List
              dataSource={consultationHistory?.data?.consultations || []}
              renderItem={(item: any) => (
                <List.Item
                  style={{ cursor: 'pointer' }}
                  onClick={() => {
                    setInputValue(item.question);
                    setSelectedCategory(item.category || '');
                  }}
                >
                  <List.Item.Meta
                    avatar={<Avatar icon={<MessageOutlined />} />}
                    title={
                      <Text ellipsis style={{ maxWidth: '150px' }}>
                        {item.question}
                      </Text>
                    }
                    description={
                      <Space direction="vertical" size="small">
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {item.category || '未分类'}
                        </Text>
                        <Text type="secondary" style={{ fontSize: '12px' }}>
                          {new Date(item.created_at).toLocaleString()}
                        </Text>
                        <div>
                          {item.status === 'completed' ? (
                            <Tag color="green" icon={<CheckCircleOutlined />}>
                              已完成
                            </Tag>
                          ) : (
                            <Tag color="orange" icon={<ClockCircleOutlined />}>
                              处理中
                            </Tag>
                          )}
                        </div>
                      </Space>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>

          {/* 系统状态 */}
          <Card title="AI模型状态" size="small">
            <List
              dataSource={[
                { name: 'DeepSeek R1', status: '正常', color: 'green' },
                { name: 'BERT模型', status: '正常', color: 'green' },
                { name: '法律分类器', status: '正常', color: 'green' },
              ]}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.name}
                    description={
                      <Tag color={item.color}>
                        {item.status}
                      </Tag>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default LegalConsultation;
