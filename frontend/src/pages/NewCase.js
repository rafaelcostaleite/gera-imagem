import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { casesAPI } from '../services/api';
import '../styles/Form.css';

function NewCase() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    case_type: 'Estou com um problema',
    service_id: null
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const caseTypes = [
    'Estou com um problema',
    'Tenho uma dúvida',
    'Quero pedir algo',
    'Solicitação de melhorias'
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await casesAPI.create(formData);
      navigate(`/cases/${response.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Erro ao criar caso');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="form-container">
      <div className="form-header">
        <h1>Novo Caso</h1>
        <button onClick={() => navigate('/')} className="btn-secondary">
          Voltar
        </button>
      </div>

      <div className="form-box">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="case_type">Tipo de Caso *</label>
            <select
              id="case_type"
              name="case_type"
              value={formData.case_type}
              onChange={handleChange}
              required
              disabled={loading}
            >
              {caseTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
            <small className="form-help">
              Selecione o tipo que melhor descreve sua necessidade
            </small>
          </div>

          <div className="form-group">
            <label htmlFor="title">Título *</label>
            <input
              type="text"
              id="title"
              name="title"
              value={formData.title}
              onChange={handleChange}
              required
              disabled={loading}
              placeholder="Descreva brevemente o caso"
            />
          </div>

          <div className="form-group">
            <label htmlFor="description">Descrição *</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              required
              disabled={loading}
              rows="6"
              placeholder="Descreva detalhadamente o caso, incluindo informações relevantes"
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <div className="form-actions">
            <button
              type="button"
              onClick={() => navigate('/')}
              className="btn-secondary"
              disabled={loading}
            >
              Cancelar
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Criando...' : 'Criar Caso'}
            </button>
          </div>
        </form>

        <div className="form-info">
          <h3>Tipos de Casos:</h3>
          <ul>
            <li><strong>Estou com um problema:</strong> Para reportar problemas e solicitar correções</li>
            <li><strong>Tenho uma dúvida:</strong> Para tirar dúvidas e obter suporte</li>
            <li><strong>Quero pedir algo:</strong> Para fazer requisições, preventivas ou intervenções</li>
            <li><strong>Solicitação de melhorias:</strong> Para sugerir melhorias em sistemas</li>
          </ul>
        </div>
      </div>
    </div>
  );
}

export default NewCase;
