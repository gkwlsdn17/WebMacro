import React, { useState, useEffect, useRef } from 'react';
import { Play, Square, Settings, RotateCcw, Calendar, Clock, Music, Volume2, VolumeX, SkipForward } from 'lucide-react';

const MelonTicketUI = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentPart, setCurrentPart] = useState('login');
  const [logs, setLogs] = useState([]);
  const [config, setConfig] = useState({
    loginInfo: { id: '', pw: '' },
    bookInfo: { 
      prodId: '', 
      bookDate: '', 
      bookTime: '', 
      order: '', 
      grade: '' 
    },
    program: {
      year: new Date().getFullYear(),
      month: new Date().getMonth() + 1,
      day: new Date().getDate(),
      hour: 14,
      minute: 0
    },
    function: {
      auto_certification: 'Y',
      special_area: 'N',
      sound: 'Y',
      seat_jump: 'N',
      seat_jump_count: 0,
      seat_jump_special_repeat: 'N',
      seat_jump_special_repeat_count: 0,
      skip_date_click: 'N'
    }
  });

  const logContainerRef = useRef(null);
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);

  // WebSocket 연결 설정 (시뮬레이션 모드)
  useEffect(() => {
    // 실제 환경에서는 Socket.IO 사용, 여기서는 시뮬레이션
    console.log('시뮬레이션 모드로 실행 중...');
    setIsConnected(true);
    
    // 시뮬레이션을 위한 초기 로그
    const initialLogs = [
      { id: 1, message: '시뮬레이션 모드로 시작되었습니다', type: 'info', timestamp: new Date().toLocaleTimeString() },
      { id: 2, message: '실제 사용시에는 Flask 서버가 필요합니다', type: 'warning', timestamp: new Date().toLocaleTimeString() }
    ];
    setLogs(initialLogs);
    
    /* 실제 환경에서 사용할 코드:
    if (typeof io !== 'undefined') {
      const newSocket = io();
      
      newSocket.on('connect', () => {
        console.log('서버에 연결되었습니다');
        setIsConnected(true);
      });
      
      newSocket.on('disconnect', () => {
        console.log('서버와의 연결이 끊어졌습니다');
        setIsConnected(false);
      });
      
      newSocket.on('log_message', (data) => {
        setLogs(prev => [...prev.slice(-49), { 
          id: Date.now(), 
          message: data.message, 
          type: data.type, 
          timestamp: data.timestamp 
        }]);
      });
      
      newSocket.on('status_update', (data) => {
        setIsRunning(data.is_running);
        setIsPaused(data.is_paused);
        setCurrentPart(data.current_part);
        setConfig(data.config);
      });
      
      setSocket(newSocket);
      
      return () => newSocket.close();
    }
    */
  }, []);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev.slice(-49), { 
      id: Date.now(), 
      message, 
      type, 
      timestamp 
    }]);
  };

  useEffect(() => {
    if (logContainerRef.current) {
      logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
    }
  }, [logs]);

  // 서버로 제어 명령 전송 (시뮬레이션 모드)
  const sendControlCommand = (command, data = {}) => {
    if (socket && isConnected) {
      // 실제 환경에서는 socket.emit 사용
      console.log('Sending command:', command, data);
    } else {
      // 시뮬레이션 모드
      console.log('시뮬레이션 - 명령어:', command, data);
      addLog(`시뮬레이션: ${command} 명령이 전송되었습니다`, 'info');
      
      // 시뮬레이션을 위한 상태 변경
      setTimeout(() => {
        if (command === 'start') {
          setIsRunning(true);
          setIsPaused(false);
          addLog('매크로가 시작되었습니다 (시뮬레이션)', 'success');
        } else if (command === 'stop') {
          setIsPaused(true);
          addLog('매크로가 일시정지되었습니다 (시뮬레이션)', 'warning');
        } else if (command === 'resume') {
          setIsPaused(false);
          addLog('매크로가 재개되었습니다 (시뮬레이션)', 'success');
        } else if (command === 'end') {
          setIsRunning(false);
          setIsPaused(false);
          setCurrentPart('login');
          addLog('매크로가 종료되었습니다 (시뮬레이션)', 'error');
        } else if (command === 'set_part') {
          setCurrentPart(data.part);
          addLog(`단계가 ${data.part}로 변경되었습니다 (시뮬레이션)`, 'info');
        }
      }, 100);
    }
  };

  const handleStart = () => {
    sendControlCommand('start');
    addLog('시작 명령을 전송했습니다.', 'info');
  };

  const handleStop = () => {
    sendControlCommand('stop');
    addLog('일시정지 명령을 전송했습니다.', 'warning');
  };

  const handleResume = () => {
    sendControlCommand('resume');
    addLog('재개 명령을 전송했습니다.', 'success');
  };

  const handleEnd = () => {
    sendControlCommand('end');
    addLog('종료 명령을 전송했습니다.', 'error');
  };

  const handleSetupPart = (part) => {
    sendControlCommand('set_part', { part });
    addLog(`단계 변경 명령을 전송했습니다: ${part}`, 'info');
  };

  const handleConfigChange = (section, field, value) => {
    sendControlCommand('update_config', { section, field, value });
    
    // 로컬 상태도 즉시 업데이트 (UI 반응성을 위해)
    setConfig(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value
      }
    }));
  };

  const handleOrderChange = (order) => {
    handleConfigChange('bookInfo', 'order', order);
    handleConfigChange('function', 'special_area', order ? 'Y' : 'N');
    addLog(`좌석 순서를 ${order || '없음'}로 설정했습니다.`, 'info');
  };

  const handleGradeChange = (grade) => {
    handleConfigChange('bookInfo', 'grade', grade);
    handleConfigChange('function', 'special_area', grade ? 'Y' : 'N');
    addLog(`좌석 등급을 ${grade || '없음'}로 설정했습니다.`, 'info');
  };

  const parts = [
    'login', 'time_wait', 'popup_check', 'click_book', 
    'change_window', 'certification', 'seat_frame_move', 
    'set_seat_jump', 'booking', 'catch'
  ];

  const getPartKorean = (part) => {
    const partMap = {
      'login': '로그인',
      'time_wait': '시간 대기',
      'popup_check': '팝업 확인',
      'click_book': '예매 클릭',
      'change_window': '창 전환',
      'certification': '보안 인증',
      'seat_frame_move': '좌석 프레임',
      'set_seat_jump': '좌석 점프 설정',
      'booking': '예매 진행',
      'catch': '예매 완료'
    };
    return partMap[part] || part;
  };

  const getLogColor = (type) => {
    switch(type) {
      case 'success': return 'text-green-600';
      case 'warning': return 'text-yellow-600';
      case 'error': return 'text-red-600';
      default: return 'text-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Music className="h-8 w-8 text-purple-600" />
              <h1 className="text-3xl font-bold text-gray-800">멜론티켓 예매 자동화</h1>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`}>
                {isConnected ? '시뮬레이션 모드' : '서버 연결 안됨'}
              </div>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${
                isRunning && !isPaused ? 'bg-green-100 text-green-800' : 
                isPaused ? 'bg-yellow-100 text-yellow-800' : 
                'bg-gray-100 text-gray-800'
              }`}>
                {isRunning && !isPaused ? '실행중' : isPaused ? '일시정지' : '대기중'}
              </div>
              <div className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                {getPartKorean(currentPart)}
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Control Panel */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">제어 패널</h2>
              
              <div className="grid grid-cols-2 gap-3 mb-6">
                <button
                  onClick={handleStart}
                  disabled={isRunning && !isPaused}
                  className="flex items-center justify-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  <Play className="h-4 w-4" />
                  <span>시작</span>
                </button>
                
                <button
                  onClick={isPaused ? handleResume : handleStop}
                  disabled={!isRunning}
                  className={`flex items-center justify-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    isPaused 
                      ? 'bg-blue-600 text-white hover:bg-blue-700' 
                      : 'bg-yellow-600 text-white hover:bg-yellow-700'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {isPaused ? <Play className="h-4 w-4" /> : <Square className="h-4 w-4" />}
                  <span>{isPaused ? '재개' : '일시정지'}</span>
                </button>
                
                <button
                  onClick={handleEnd}
                  className="flex items-center justify-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors col-span-2"
                >
                  <Square className="h-4 w-4" />
                  <span>종료</span>
                </button>
              </div>

              {/* Part Selection */}
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-2">단계 선택</label>
                <select
                  value={currentPart}
                  onChange={(e) => handleSetupPart(e.target.value)}
                  className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  {parts.map(part => (
                    <option key={part} value={part}>{getPartKorean(part)}</option>
                  ))}
                </select>
              </div>

              {/* Quick Actions */}
              <div className="space-y-3">
                <h3 className="text-lg font-medium text-gray-800">빠른 설정</h3>
                
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">좌석 순서 (예: A,B,C)</label>
                  <input
                    type="text"
                    value={config.bookInfo.order}
                    onChange={(e) => handleOrderChange(e.target.value)}
                    placeholder="A,B,C"
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="block text-sm font-medium text-gray-700">좌석 등급 (예: S석,A석)</label>
                  <input
                    type="text"
                    value={config.bookInfo.grade}
                    onChange={(e) => handleGradeChange(e.target.value)}
                    placeholder="S석,A석,B석"
                    className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <span className="text-sm font-medium text-gray-700">날짜 선택 건너뛰기</span>
                  <button
                    onClick={() => handleConfigChange('function', 'skip_date_click', config.function.skip_date_click === 'Y' ? 'N' : 'Y')}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      config.function.skip_date_click === 'Y' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {config.function.skip_date_click === 'Y' ? '사용' : '미사용'}
                  </button>
                </div>
              </div>
            </div>

            {/* Settings Panel */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>설정</span>
              </h2>
              
              <div className="space-y-4">
                {/* Sound Toggle */}
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700 flex items-center space-x-2">
                    {config.function.sound === 'Y' ? <Volume2 className="h-4 w-4" /> : <VolumeX className="h-4 w-4" />}
                    <span>완료 사운드</span>
                  </span>
                  <button
                    onClick={() => handleConfigChange('function', 'sound', config.function.sound === 'Y' ? 'N' : 'Y')}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      config.function.sound === 'Y' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {config.function.sound === 'Y' ? '사용' : '미사용'}
                  </button>
                </div>

                {/* Seat Jump */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700 flex items-center space-x-2">
                      <SkipForward className="h-4 w-4" />
                      <span>좌석 점프</span>
                    </span>
                    <button
                      onClick={() => handleConfigChange('function', 'seat_jump', config.function.seat_jump === 'Y' ? 'N' : 'Y')}
                      className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                        config.function.seat_jump === 'Y' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-600'
                      }`}
                    >
                      {config.function.seat_jump === 'Y' ? '사용' : '미사용'}
                    </button>
                  </div>
                  
                  {config.function.seat_jump === 'Y' && (
                    <input
                      type="number"
                      value={config.function.seat_jump_count}
                      onChange={(e) => handleConfigChange('function', 'seat_jump_count', parseInt(e.target.value) || 0)}
                      placeholder="점프할 좌석 수"
                      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 text-sm"
                    />
                  )}
                </div>

                {/* Auto Certification */}
                <div className="flex items-center justify-between">
                  <span className="text-sm font-medium text-gray-700">자동 보안인증</span>
                  <button
                    onClick={() => handleConfigChange('function', 'auto_certification', config.function.auto_certification === 'Y' ? 'N' : 'Y')}
                    className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      config.function.auto_certification === 'Y' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {config.function.auto_certification === 'Y' ? '사용' : '미사용'}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Configuration Form */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-4">예매 설정</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* Login Info */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-700">로그인 정보</h3>
                  <input
                    type="text"
                    value={config.loginInfo.id}
                    onChange={(e) => handleConfigChange('loginInfo', 'id', e.target.value)}
                    placeholder="아이디"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <input
                    type="password"
                    value={config.loginInfo.pw}
                    onChange={(e) => handleConfigChange('loginInfo', 'pw', e.target.value)}
                    placeholder="비밀번호"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>

                {/* Book Info */}
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-gray-700">예매 정보</h3>
                  <input
                    type="text"
                    value={config.bookInfo.prodId}
                    onChange={(e) => handleConfigChange('bookInfo', 'prodId', e.target.value)}
                    placeholder="상품 ID"
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <input
                    type="date"
                    value={config.bookInfo.bookDate}
                    onChange={(e) => handleConfigChange('bookInfo', 'bookDate', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <input
                    type="time"
                    value={config.bookInfo.bookTime}
                    onChange={(e) => handleConfigChange('bookInfo', 'bookTime', e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>

              {/* Schedule Info */}
              <div className="mt-6">
                <h3 className="text-lg font-medium text-gray-700 mb-4 flex items-center space-x-2">
                  <Calendar className="h-5 w-5" />
                  <span>예매 시작 시간</span>
                </h3>
                <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                  <input
                    type="number"
                    value={config.program.year}
                    onChange={(e) => handleConfigChange('program', 'year', parseInt(e.target.value))}
                    placeholder="년"
                    className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <input
                    type="number"
                    value={config.program.month}
                    onChange={(e) => handleConfigChange('program', 'month', parseInt(e.target.value))}
                    placeholder="월"
                    min="1"
                    max="12"
                    className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <input
                    type="number"
                    value={config.program.day}
                    onChange={(e) => handleConfigChange('program', 'day', parseInt(e.target.value))}
                    placeholder="일"
                    min="1"
                    max="31"
                    className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <input
                    type="number"
                    value={config.program.hour}
                    onChange={(e) => handleConfigChange('program', 'hour', parseInt(e.target.value))}
                    placeholder="시"
                    min="0"
                    max="23"
                    className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                  <input
                    type="number"
                    value={config.program.minute}
                    onChange={(e) => handleConfigChange('program', 'minute', parseInt(e.target.value))}
                    placeholder="분"
                    min="0"
                    max="59"
                    className="p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                  />
                </div>
              </div>
            </div>

            {/* Logs */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-800">실행 로그</h2>
                <button
                  onClick={() => setLogs([])}
                  className="flex items-center space-x-2 text-gray-500 hover:text-gray-700 transition-colors"
                >
                  <RotateCcw className="h-4 w-4" />
                  <span className="text-sm">로그 초기화</span>
                </button>
              </div>
              
              <div
                ref={logContainerRef}
                className="bg-gray-50 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm space-y-1"
              >
                {logs.length === 0 ? (
                  <div className="text-gray-500 text-center py-8">로그가 없습니다.</div>
                ) : (
                  logs.map(log => (
                    <div key={log.id} className="flex items-start space-x-3">
                      <span className="text-gray-400 text-xs w-20 flex-shrink-0">
                        {log.timestamp}
                      </span>
                      <span className={`${getLogColor(log.type)} flex-1`}>
                        {log.message}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MelonTicketUI;