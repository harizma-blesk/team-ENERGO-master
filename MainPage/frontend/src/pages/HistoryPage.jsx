import { useMemo, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Alert, Button, Card, Drawer, Space, Table, Tag, Typography } from 'antd';
import { loadHistory, loadHistoryDetails } from '../api/history-api';

const attemptOrdinalLabel = (n) => {
  const labels = {
    1: 'Первая попытка',
    2: 'Вторая попытка',
    3: 'Третья попытка',
    4: 'Четвёртая попытка',
    5: 'Пятая попытка'
  };
  if (labels[n]) {
    return labels[n];
  }
  return `${n}-я попытка`;
};

const HistoryPage = () => {
  const [selectedAttemptId, setSelectedAttemptId] = useState(null);

  const historyQuery = useQuery({
    queryKey: ['history'],
    queryFn: () => loadHistory({ page: 1, pageSize: 50 })
  });

  const detailsQuery = useQuery({
    queryKey: ['history-details', selectedAttemptId],
    queryFn: () => loadHistoryDetails(selectedAttemptId),
    enabled: Boolean(selectedAttemptId)
  });

  const rows = useMemo(() => {
    const items = (historyQuery.data?.items ?? []);
    const map = new Map();
    [...items]
      .sort((a, b) => {
        const aTime = a.submittedAt ? new Date(a.submittedAt).getTime() : 0;
        const bTime = b.submittedAt ? new Date(b.submittedAt).getTime() : 0;
        return aTime - bTime;
      })
      .forEach((item, idx) => {
        map.set(item.attemptId, idx + 1);
      });

    return items.map((item) => ({
      ...item,
      attemptOrder: map.get(item.attemptId) ?? 1
    }));
  }, [historyQuery.data?.items]);

  const selectedAttemptOrder = useMemo(
    () => rows.find((row) => row.attemptId === selectedAttemptId)?.attemptOrder ?? null,
    [rows, selectedAttemptId]
  );

  const columns = [
    {
      title: 'Попытка',
      dataIndex: 'attemptOrder',
      render: (value) => attemptOrdinalLabel(value)
    },
    {
      title: 'Процент',
      dataIndex: 'scorePercent',
      render: (value) => `${value ?? 0}%`
    },
    {
      title: 'Статус',
      dataIndex: 'passed',
      render: (passed) => <Tag color={passed ? 'green' : 'red'}>{passed ? 'Зачёт' : 'Незачёт'}</Tag>
    },
    {
      title: 'Дата',
      dataIndex: 'submittedAt',
      render: (value) => (value ? new Date(value).toLocaleString() : '-')
    },
    {
      title: 'Действие',
      dataIndex: 'attemptId',
      render: (value) => <Button onClick={() => setSelectedAttemptId(value)}>Открыть</Button>
    }
  ];

  return (
    <Space direction="vertical" size="large" style={{ width: '100%' }}>
      <Card>
        <Typography.Title level={3}>История попыток</Typography.Title>
      </Card>

      {historyQuery.error ? <Alert type="error" showIcon message="Не удалось загрузить историю." /> : null}

      <Card>
        <Table
          rowKey="attemptId"
          loading={historyQuery.isLoading}
          dataSource={rows}
          columns={columns}
          pagination={false}
        />
      </Card>

      <Drawer
        title="Детали попытки"
        open={Boolean(selectedAttemptId)}
        onClose={() => setSelectedAttemptId(null)}
        width={640}
      >
        {detailsQuery.isLoading ? <Typography.Text>Загрузка...</Typography.Text> : null}
        {detailsQuery.data ? (
          <Space direction="vertical" style={{ width: '100%' }}>
            <Typography.Text strong>
              Попытка: {attemptOrdinalLabel(selectedAttemptOrder ?? 1)}
            </Typography.Text>
            <Typography.Paragraph>{detailsQuery.data.feedback?.summary}</Typography.Paragraph>
                          {(detailsQuery.data.answers ?? []).map((answer) => {
                const question = (detailsQuery.data.questions ?? []).find((q) => q.id === answer.questionId);
                return (
                  <Card size="small" key={answer.questionId}>
                    <Typography.Text strong>{question?.text ?? answer.questionId}</Typography.Text>
                    <br />
                    <Typography.Text type="secondary">Баллы: {answer.score ?? 0}</Typography.Text>
                    <br />
                    <Typography.Text>{answer.rationale}</Typography.Text>
                  </Card>
                );
              })}
          </Space>
        ) : null}
      </Drawer>
    </Space>
  );
};

export default HistoryPage;
