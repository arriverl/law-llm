import React, { useState } from 'react';
import {
  Card,
  Input,
  Button,
  List,
  Tag,
  Space,
  Typography,
  Select,
  Upload,
  message,
  Modal,
  Form,
  Row,
  Avatar,
  Col,
  Divider,
  Progress,
} from 'antd';
import {
  SearchOutlined,
  PlusOutlined,
  UploadOutlined,
  BookOutlined,
  TagOutlined,
  FileTextOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
} from '@ant-design/icons';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { knowledgeAPI } from '../services/api';
import ReactMarkdown from 'react-markdown';

const { Title, Text } = Typography;
const { Search } = Input;
const { Option } = Select;
const { TextArea } = Input;

interface KnowledgeItem {
  id: number;
  title: string;
  content: string;
  category: string;
  tags: string[];
  source: string;
  version: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

const KnowledgeBase: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingItem, setEditingItem] = useState<KnowledgeItem | null>(null);
  const [form] = Form.useForm();
  const queryClient = useQueryClient();

  // 获取知识库列表
  const { data: knowledgeData, isLoading } = useQuery(
    ['knowledge', selectedCategory],
    () => knowledgeAPI.getKnowledge(selectedCategory, 0, 50)
  );

  // 获取分类列表
  const { data: categories } = useQuery('knowledge-categories', knowledgeAPI.getCategories);

  // 搜索知识库
  const { data: searchResults, isLoading: searchLoading } = useQuery(
    ['knowledge-search', searchQuery, selectedCategory, selectedTags],
    () => knowledgeAPI.searchKnowledge(searchQuery, selectedCategory, selectedTags, 20),
    {
      enabled: !!searchQuery,
    }
  );

  // 创建知识条目
  const createMutation = useMutation(knowledgeAPI.createKnowledge, {
    onSuccess: () => {
      message.success('知识条目创建成功');
      setIsModalVisible(false);
      form.resetFields();
      queryClient.invalidateQueries('knowledge');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '创建失败');
    },
  });

  // 更新知识条目
  const updateMutation = useMutation(
    ({ id, data }: { id: number; data: any }) => knowledgeAPI.updateKnowledge(id, data),
    {
      onSuccess: () => {
        message.success('知识条目更新成功');
        setIsModalVisible(false);
        setEditingItem(null);
        form.resetFields();
        queryClient.invalidateQueries('knowledge');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '更新失败');
      },
    }
  );

  // 删除知识条目
  const deleteMutation = useMutation(knowledgeAPI.deleteKnowledge, {
    onSuccess: () => {
      message.success('知识条目删除成功');
      queryClient.invalidateQueries('knowledge');
    },
    onError: (error: any) => {
      message.error(error.response?.data?.detail || '删除失败');
    },
  });

  // 文件上传
  const uploadMutation = useMutation(
    ({ file, category }: { file: File; category: string }) => knowledgeAPI.uploadFile(file, category),
    {
      onSuccess: () => {
        message.success('文件上传成功，正在处理中');
        queryClient.invalidateQueries('knowledge');
      },
      onError: (error: any) => {
        message.error(error.response?.data?.detail || '上传失败');
      },
    }
  );

  const handleCreate = () => {
    setEditingItem(null);
    form.resetFields();
    setIsModalVisible(true);
  };

  const handleEdit = (item: KnowledgeItem) => {
    setEditingItem(item);
    form.setFieldsValue({
      title: item.title,
      content: item.content,
      category: item.category,
      tags: item.tags,
      source: item.source,
    });
    setIsModalVisible(true);
  };

  const handleDelete = (id: number) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除这个知识条目吗？',
      onOk: () => deleteMutation.mutate(id),
    });
  };

  const handleSubmit = (values: any) => {
    if (editingItem) {
      updateMutation.mutate({ id: editingItem.id, data: values });
    } else {
      createMutation.mutate(values);
    }
  };

  const handleFileUpload = (file: File) => {
    const category = selectedCategory || 'general';
    uploadMutation.mutate({ file, category });
    return false; // 阻止默认上传行为
  };

  const displayData = searchQuery ? searchResults : knowledgeData;

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>
        法律知识库
      </Title>

      {/* 搜索和筛选 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} md={8}>
            <Search
              placeholder="搜索知识库..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onSearch={setSearchQuery}
              enterButton={<SearchOutlined />}
            />
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Select
              placeholder="选择分类"
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
          </Col>
          <Col xs={24} sm={12} md={6}>
            <Space>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleCreate}
              >
                新建知识
              </Button>
              <Upload
                beforeUpload={handleFileUpload}
                showUploadList={false}
                accept=".txt,.pdf,.docx"
              >
                <Button icon={<UploadOutlined />}>
                  上传文件
                </Button>
              </Upload>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 知识库列表 */}
      <Card>
        <List
          loading={isLoading || searchLoading}
          dataSource={displayData?.data || []}
          renderItem={(item: KnowledgeItem) => (
            <List.Item
              actions={[
                <Button
                  type="text"
                  icon={<EyeOutlined />}
                  onClick={() => {
                    Modal.info({
                      title: item.title,
                      content: (
                        <div>
                          <ReactMarkdown>{item.content}</ReactMarkdown>
                          <Divider />
                          <Space>
                            <Tag icon={<TagOutlined />}>{item.category}</Tag>
                            <Text type="secondary">来源: {item.source}</Text>
                            <Text type="secondary">版本: {item.version}</Text>
                          </Space>
                        </div>
                      ),
                      width: 800,
                    });
                  }}
                >
                  查看
                </Button>,
                <Button
                  type="text"
                  icon={<EditOutlined />}
                  onClick={() => handleEdit(item)}
                >
                  编辑
                </Button>,
                <Button
                  type="text"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleDelete(item.id)}
                >
                  删除
                </Button>,
              ]}
        >
          <List.Item.Meta
            avatar={<Avatar icon={<BookOutlined />} />}
            title={
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Text strong>{item.title}</Text>
                <Tag color="blue">{item.category}</Tag>
              </div>
            }
            description={
              <div>
                <Text ellipsis style={{ display: 'block', marginBottom: '8px' }}>
                  {item.content.length > 200 ? `${item.content.substring(0, 200)}...` : item.content}
                </Text>
                <Space wrap>
                  {item.tags.map((tag) => (
                    <Tag key={tag} icon={<TagOutlined />}>
                      {tag}
                    </Tag>
                  ))}
                </Space>
                <div style={{ marginTop: '8px' }}>
                  <Text type="secondary" style={{ fontSize: '12px' }}>
                    来源: {item.source} | 版本: {item.version} | 
                    创建时间: {new Date(item.created_at).toLocaleString()}
                  </Text>
                </div>
              </div>
            }
          />
        </List.Item>
      )}
    />
  </Card>

  {/* 创建/编辑模态框 */}
  <Modal
    title={editingItem ? '编辑知识条目' : '新建知识条目'}
    open={isModalVisible}
    onCancel={() => {
      setIsModalVisible(false);
      setEditingItem(null);
      form.resetFields();
    }}
    footer={null}
    width={800}
  >
    <Form
      form={form}
      layout="vertical"
      onFinish={handleSubmit}
    >
      <Form.Item
        name="title"
        label="标题"
        rules={[{ required: true, message: '请输入标题' }]}
      >
        <Input placeholder="请输入知识条目标题" />
      </Form.Item>

      <Form.Item
        name="content"
        label="内容"
        rules={[{ required: true, message: '请输入内容' }]}
      >
        <TextArea
          rows={6}
          placeholder="请输入知识条目内容，支持Markdown格式"
        />
      </Form.Item>

      <Row gutter={16}>
        <Col span={12}>
          <Form.Item
            name="category"
            label="分类"
            rules={[{ required: true, message: '请选择分类' }]}
          >
            <Select placeholder="请选择分类">
              {categories?.data?.categories?.map((category: any) => (
                <Option key={category.id} value={category.id}>
                  {category.name}
                </Option>
              ))}
            </Select>
          </Form.Item>
        </Col>
        <Col span={12}>
          <Form.Item
            name="source"
            label="来源"
            rules={[{ required: true, message: '请输入来源' }]}
          >
            <Input placeholder="请输入知识来源" />
          </Form.Item>
        </Col>
      </Row>

      <Form.Item
        name="tags"
        label="标签"
      >
        <Select
          mode="tags"
          placeholder="请输入标签，按回车添加"
          style={{ width: '100%' }}
        />
      </Form.Item>

      <Form.Item>
        <Space>
          <Button
            type="primary"
            htmlType="submit"
            loading={createMutation.isLoading || updateMutation.isLoading}
          >
            {editingItem ? '更新' : '创建'}
          </Button>
          <Button onClick={() => setIsModalVisible(false)}>
            取消
          </Button>
        </Space>
      </Form.Item>
    </Form>
  </Modal>
</div>
);
};

export default KnowledgeBase;
