import React, { useState } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Typography,
  Space,
  Avatar,
  Upload,
  message,
  Divider,
  Row,
  Col,
  Tag,
  Statistic,
  List,
} from 'antd';
import {
  UserOutlined,
  MailOutlined,
  PhoneOutlined,
  EditOutlined,
  SaveOutlined,
  CameraOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { authAPI, legalAIAPI } from '../services/api';
import { useAuthStore } from '../stores/authStore';

const { Title, Text } = Typography;

const Profile: React.FC = () => {
  const [isEditing, setIsEditing] = useState(false);
  const [form] = Form.useForm();
  const { user, updateUser } = useAuthStore();
  const queryClient = useQueryClient();

  // 获取用户详细信息
  const { data: userData, isLoading } = useQuery(
    'user-profile',
    authAPI.getCurrentUser
  );

  // 获取用户咨询统计
  const { data: consultationStats } = useQuery(
    'user-consultation-stats',
    () => legalAIAPI.getConsultations(0, 1000)
  );

  // 更新用户信息
  const updateMutation = useMutation(
    (data: any) => authAPI.getCurrentUser(), // 这里应该调用实际的更新API
    {
      onSuccess: (response) => {
        message.success('个人信息更新成功');
        setIsEditing(false);
        updateUser(response.data);
        queryClient.invalidateQueries('user-profile');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '更新失败');
      },
    }
  );

  const handleEdit = () => {
    setIsEditing(true);
    form.setFieldsValue({
      username: userData?.data?.username,
      email: userData?.data?.email,
      full_name: userData?.data?.full_name,
    });
  };

  const handleSave = (values: any) => {
    updateMutation.mutate(values);
  };

  const handleCancel = () => {
    setIsEditing(false);
    form.resetFields();
  };

  const handleAvatarUpload = (file: File) => {
    // 这里实现头像上传逻辑
    message.info('头像上传功能开发中...');
    return false;
  };

  const getRoleName = (role: string) => {
    switch (role) {
      case 'admin':
        return '系统管理员';
      case 'lawyer':
        return '律师';
      case 'enterprise':
        return '企业用户';
      default:
        return '普通用户';
    }
  };

  const getRoleColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'red';
      case 'lawyer':
        return 'blue';
      case 'enterprise':
        return 'green';
      default:
        return 'default';
    }
  };

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>
        个人资料
      </Title>

      <Row gutter={[24, 24]}>
        {/* 个人信息 */}
        <Col xs={24} lg={16}>
          <Card
            title="基本信息"
            extra={
              !isEditing ? (
                <Button icon={<EditOutlined />} onClick={handleEdit}>
                  编辑
                </Button>
              ) : (
                <Space>
                  <Button onClick={handleCancel}>取消</Button>
                  <Button
                    type="primary"
                    icon={<SaveOutlined />}
                    onClick={() => form.submit()}
                    loading={updateMutation.isLoading}
                  >
                    保存
                  </Button>
                </Space>
              )
            }
          >
            <Form
              form={form}
              layout="vertical"
              onFinish={handleSave}
              disabled={!isEditing}
            >
              <Row gutter={16}>
                <Col span={24}>
                  <div style={{ textAlign: 'center', marginBottom: '24px' }}>
                    <Avatar
                      size={80}
                      icon={<UserOutlined />}
                      style={{ marginBottom: '16px' }}
                    />
                    <div>
                      <Upload
                        beforeUpload={handleAvatarUpload}
                        showUploadList={false}
                      >
                        <Button icon={<CameraOutlined />} type="link">
                          更换头像
                        </Button>
                      </Upload>
                    </div>
                  </div>
                </Col>
              </Row>

              <Row gutter={16}>
                <Col span={12}>
                  <Form.Item
                    name="username"
                    label="用户名"
                    rules={[{ required: true, message: '请输入用户名' }]}
                  >
                    <Input prefix={<UserOutlined />} />
                  </Form.Item>
                </Col>
                <Col span={12}>
                  <Form.Item
                    name="email"
                    label="邮箱"
                    rules={[
                      { required: true, message: '请输入邮箱' },
                      { type: 'email', message: '请输入有效的邮箱地址' }
                    ]}
                  >
                    <Input prefix={<MailOutlined />} />
                  </Form.Item>
                </Col>
              </Row>

              <Form.Item
                name="full_name"
                label="姓名"
              >
                <Input prefix={<UserOutlined />} />
              </Form.Item>

              <Divider />

              <div>
                <Text type="secondary">用户角色：</Text>
                <Tag color={getRoleColor(userData?.data?.role || '')} style={{ marginLeft: '8px' }}>
                  {getRoleName(userData?.data?.role || '')}
                </Tag>
              </div>

              <div style={{ marginTop: '8px' }}>
                <Text type="secondary">账户状态：</Text>
                <Tag color={userData?.data?.is_active ? 'green' : 'red'} style={{ marginLeft: '8px' }}>
                  {userData?.data?.is_active ? '活跃' : '非活跃'}
                </Tag>
              </div>
            </Form>
          </Card>
        </Col>

        {/* 统计信息 */}
        <Col xs={24} lg={8}>
          <Card title="使用统计">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Statistic
                  title="总咨询次数"
                  value={consultationStats?.data?.total || 0}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Col>
              <Col span={12}>
                <Statistic
                  title="本月咨询"
                  value={consultationStats?.data?.consultations?.filter((item: any) => {
                    const itemDate = new Date(item.created_at);
                    const now = new Date();
                    return itemDate.getMonth() === now.getMonth() && 
                           itemDate.getFullYear() === now.getFullYear();
                  }).length || 0}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Col>
            </Row>
          </Card>

          <Card title="账户信息" style={{ marginTop: '16px' }}>
            <List
              dataSource={[
                { label: '注册时间', value: userData?.data?.created_at ? new Date(userData.data.created_at).toLocaleDateString() : '未知' },
                { label: '最后登录', value: '刚刚' },
                { label: '账户类型', value: getRoleName(userData?.data?.role || '') },
              ]}
              renderItem={(item) => (
                <List.Item>
                  <List.Item.Meta
                    title={item.label}
                    description={<Text strong>{item.value}</Text>}
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {/* 最近活动 */}
      <Card title="最近活动" style={{ marginTop: '24px' }}>
        <List
          dataSource={consultationStats?.data?.consultations?.slice(0, 5) || []}
          renderItem={(item: any) => (
            <List.Item>
              <List.Item.Meta
                avatar={<Avatar icon={<UserOutlined />} />}
                title={
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Text ellipsis style={{ maxWidth: '300px' }}>
                      {item.question}
                    </Text>
                    <Tag color={item.status === 'completed' ? 'green' : 'orange'}>
                      {item.status === 'completed' ? '已完成' : '处理中'}
                    </Tag>
                  </div>
                }
                description={
                  <div>
                    <Text type="secondary" style={{ fontSize: '12px' }}>
                      分类: {item.category || '未分类'} | 
                      置信度: {Math.round((parseFloat(item.confidence) || 0) * 100)}% | 
                      {new Date(item.created_at).toLocaleString()}
                    </Text>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default Profile;
