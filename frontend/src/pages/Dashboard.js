import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { casesAPI } from '../services/api';
import '../styles/Dashboard.css';

function Dashboard() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    try {
      setLoading(true);
      const response = await casesAPI.getMyCases();
      setCases(response.data);
    } catch (err) {
      setError('Erro ao carregar casos');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      'Aberto': '#3498db',
      'Em atendimento': '#f39c12',
      'Solucionado': '#2ecc71',
      'Concluído': '#95a5a6',
      'Cancelado': '#e74c3c'
    };
    return colors[status] || '#95a5a6';
  };

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Carregando...</div>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Meus Casos</h1>
        <Link to="/cases/new" className="btn-primary">Novo Caso</Link>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="dashboard-stats">
        <div className="stat-card">
          <h3>Total de Casos</h3>
          <p className="stat-number">{cases.length}</p>
        </div>
        <div className="stat-card">
          <h3>Abertos</h3>
          <p className="stat-number">
            {cases.filter(c => c.status === 'Aberto').length}
          </p>
        </div>
        <div className="stat-card">
          <h3>Em Atendimento</h3>
          <p className="stat-number">
            {cases.filter(c => c.status === 'Em atendimento').length}
          </p>
        </div>
        <div className="stat-card">
          <h3>Solucionados</h3>
          <p className="stat-number">
            {cases.filter(c => c.status === 'Solucionado').length}
          </p>
        </div>
      </div>

      <div className="cases-list">
        {cases.length === 0 ? (
          <div className="empty-state">
            <p>Você não tem casos no momento</p>
            <Link to="/cases/new" className="btn-primary">Criar Primeiro Caso</Link>
          </div>
        ) : (
          <table className="cases-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Título</th>
                <th>Tipo</th>
                <th>Status</th>
                <th>Categoria</th>
                <th>Técnico</th>
                <th>Horas</th>
                <th>Criado em</th>
                <th>Ações</th>
              </tr>
            </thead>
            <tbody>
              {cases.map((caseItem) => (
                <tr key={caseItem.id}>
                  <td>#{caseItem.id}</td>
                  <td>{caseItem.title}</td>
                  <td>{caseItem.case_type}</td>
                  <td>
                    <span
                      className="status-badge"
                      style={{ backgroundColor: getStatusColor(caseItem.status) }}
                    >
                      {caseItem.status}
                    </span>
                  </td>
                  <td>{caseItem.category || '-'}</td>
                  <td>{caseItem.technician_name || '-'}</td>
                  <td>{caseItem.total_hours?.toFixed(2) || '0.00'}h</td>
                  <td>{new Date(caseItem.created_at).toLocaleDateString('pt-BR')}</td>
                  <td>
                    <Link to={`/cases/${caseItem.id}`} className="btn-small">
                      Ver Detalhes
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
