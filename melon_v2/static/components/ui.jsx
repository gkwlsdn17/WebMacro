// ui.jsx - config.ini 로드 문제 해결된 버전
// static/components/ui.jsx 로 저장하세요

const MelonTicketUI = () => {
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentPart, setCurrentPart] = useState('login');
  const [logs, setLogs] = useState([]);
  const [config, setConfig] = useState({
    loginInfo: { id: '', pw: '' },
    bookInfo: { 
      prod_id: '', 
      book_date: '', 
      book_time: '', 
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
  const [isConfigLoaded, setIsConfigLoaded] = useState(false);

  // 설정 로드 함수
  const loadConfigFromServer = async () => {
    try {
      const response = await fetch('/api/config');
      if (response.ok) {
        const serverConfig = await response.json();
        console.log('서버에서 설정 로드:', serverConfig);
        setConfig(serverConfig);
        setIsConfigLoaded(true);
        addLog('✅ 서버에서 설정을 로드했습니다.', 'success');
        
        // prod_id 확인
        if (serverConfig.bookInfo && serverConfig.bookInfo.prod_id) {
          addLog(`📦 상품ID 확인: ${serverConfig.bookInfo.prod_id}`, 'info');
        } else {
          addLog('⚠️ 상품ID가 설정되지 않았습니다.', 'warning');
        }
        
        return serverConfig;
      } else {
        throw new Error('설정 로드 실패');
      }
    } catch (error) {
      console.error('설정 로드 에러:', error);
      addLog('❌ 설정 로드에 실패했습니다.', 'error');
      return null;
    }
  };

  // 설정 다시 로드 함수
  const reloadConfig = async () => {
    addLog('🔄 config.ini에서 설정을 다시 로드합니다...', 'info');
    try {
      const response = await fetch('/api/config/reload', { method: 'POST' });
      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          setConfig(result.config);
          addLog('✅ config.ini 설정이 성공적으로 다시 로드되었습니다.', 'success');
          
          // prod_id 확인
          if (result.config.bookInfo && result.config.bookInfo.prod_id) {
            addLog(`📦 상품ID: ${result.config.bookInfo.prod_id}`, 'info');
          }
        } else {
          addLog(`❌ 설정 재로드 실패: ${result.error}`, 'error');
        }
      }
    } catch (error) {
      console.error('설정 재로드 에러:', error);
      addLog('❌ 설정 재로드 중 오류가 발생했습니다.', 'error');
    }
  };

  // WebSocket 연결 설정
  useEffect(() => {
    if (typeof io !== 'undefined') {
      const newSocket = io();
      
      newSocket.on('connect', () => {
        console.log('서버에 연결되었습니다');
        setIsConnected(true);
        addLog('🔗 서버에 연결되었습니다', 'success');
        
        // 연결되면 즉시 현재 설정 요청
        newSocket.emit('request_config');
      });
      
      newSocket.on('disconnect', () => {
        console.log('서버와의 연결이 끊어졌습니다');
        setIsConnected(false);
        addLog('🔌 서버와의 연결이 끊어졌습니다', 'warning');
      });
      
      newSocket.on('log_message', (data) => {
        setLogs(prev => [...prev.slice(-49), { 
          id: Date.now() + Math.random(), 
          message: data.message, 
          type: data.type, 
          timestamp: data.timestamp 
        }]);
      });
      
      newSocket.on('status_update', (data) => {
        console.log('Status update received:', data);
        setIsRunning(data.is_running);
        setIsPaused(data.is_paused);
        setCurrentPart(data.current_part);
        
        // 설정 데이터가 있을 때만 업데이트 - 전체 교체 방식으로 수정
        if (data.config) {
          console.log('Config update from server:', data.config);
          setConfig(data.config);
          setIsConfigLoaded(true);
          
          // prod_id 로깅
          if (data.config.bookInfo && data.config.bookInfo.prod_id) {
            console.log('prod_id received:', data.config.bookInfo.prod_id);
          }
        }
      });
      
      setSocket(newSocket);
      
      return () => newSocket.close();
    } else {
      // Socket.IO가 로드되지 않은 경우 시뮬레이션 모드
      console.log('Socket.IO를 찾을 수 없습니다. 시뮬레이션 모드로 실행합니다.');
      setIsConnected(true);
      const initialLogs = [
        { id: 1, message: '⚠️ Socket.IO 시뮬레이션 모드로 시작되었습니다', type: 'warning', timestamp: new Date().toLocaleTimeString() },
        { id: 2, message: '📡 실제 사용시에는 Flask 서버가 필요합니다', type: 'info', timestamp: new Date().toLocaleTimeString() }
      ];
      setLogs(initialLogs);
      
      // 시뮬레이션 모드에서도 HTTP API로 설정 로드 시도
      loadConfigFromServer();
    }
  }, []);

  // 컴포넌트 마운트 시 설정 로드
  useEffect(() => {
    if (!socket && !isConfigLoaded) {
      loadConfigFromServer();
    }
  }, [socket, isConfigLoaded]);

  const addLog = (message, type = 'info') => {
    const timestamp = new Date().toLocaleTimeString();
    setLogs(prev => [...prev.slice(-49), { 
      id: Date.now() + Math.random(), 
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

  // 서버로 제어 명령 전송
  const sendControlCommand = (command, data = {}) => {
    if (socket && isConnected) {
      socket.emit('control_command', { command, ...data });
      console.log('서버로 명령 전송:', command, data);
    } else {
      // 시뮬레이션 모드 또는 HTTP API 사용
      console.log('WebSocket 없음 - HTTP API 시도:', command, data);
      
      if (command === 'update_config') {
        // HTTP API로 설정 업데이트
        fetch('/api/config', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        }).then(response => response.json())
          .then(result => {
            if (result.success) {
              console.log('HTTP API로 설정 업데이트 성공');
            }
          }).catch(error => {
            console.error('HTTP API 설정 업데이트 실패:', error);
          });
      } else {
        // 다른 명령들은 시뮬레이션
        addLog(`시뮬레이션: ${command} 명령이 전송되었습니다`, 'info');
        
        setTimeout(() => {
          if (command === 'start') {
            setIsRunning(true);
            setIsPaused(false);
            addLog('🚀 매크로가 시작되었습니다 (시뮬레이션)', 'success');
          } else if (command === 'stop') {
            setIsPaused(true);
            addLog('⏸️ 매크로가 일시정지되었습니다 (시뮬레이션)', 'warning');
          } else if (command === 'resume') {
            setIsPaused(false);
            addLog('▶️ 매크로가 재개되었습니다 (시뮬레이션)', 'success');
          } else if (command === 'end') {
            setIsRunning(false);
            setIsPaused(false);
            setCurrentPart('login');
            addLog('🛑 매크로가 종료되었습니다 (시뮬레이션)', 'error');
          } else if (command === 'set_part') {
            setCurrentPart(data.part);
            addLog(`📍 단계가 ${data.part}로 변경되었습니다 (시뮬레이션)`, 'info');
          }
        }, 100);
      }
    }
  };

  const handleStart = () => {
    // 시작 전 필수 값 검증
    if (!config.loginInfo.id) {
      addLog('❌ 아이디를 입력해주세요.', 'error');
      return;
    }
    if (!config.loginInfo.pw) {
      addLog('❌ 비밀번호를 입력해주세요.', 'error');
      return;
    }
    if (!config.bookInfo.prod_id) {
      addLog('❌ 상품 ID를 입력해주세요.', 'error');
      return;
    }
    
    sendControlCommand('start');
    addLog('📤 시작 명령을 전송했습니다.', 'info');
  };

  const handleStop = () => {
    sendControlCommand('stop');
    addLog('📤 일시정지 명령을 전송했습니다.', 'warning');
  };

  const handleResume = () => {
    sendControlCommand('resume');
    addLog('📤 재개 명령을 전송했습니다.', 'success');
  };

  const handleEnd = () => {
    sendControlCommand('end');
    addLog('📤 종료 명령을 전송했습니다.', 'error');
  };

  const handleSetupPart = (part) => {
    sendControlCommand('set_part', { part });
    addLog(`📤 단계 변경 명령을 전송했습니다: ${part}`, 'info');
  };

  const handleConfigChange = (section, field, value) => {
    console.log('Config change:', section, field, value);
    
    // 서버로 변경사항 전송
    sendControlCommand('update_config', { section, field, value });
    
    // 로컬 상태 즉시 업데이트 (UI 반응성을 위해)
    setConfig(prevConfig => ({
      ...prevConfig,
      [section]: {
        ...prevConfig[section],
        [field]: value
      }
    }));
  };

  const handleOrderChange = (order) => {
    handleConfigChange('bookInfo', 'order', order);
    if (order && order.trim()) {
      handleConfigChange('function', 'special_area', 'Y');
      addLog(`🎯 좌석 순서를 ${order}로 설정했습니다. (특별구역 활성화)`, 'info');
    } else {
      // order가 비어있고 grade도 비어있으면 special_area 비활성화
      if (!config.bookInfo.grade || !config.bookInfo.grade.trim()) {
        handleConfigChange('function', 'special_area', 'N');
      }
      addLog('🔄 좌석 순서를 제거했습니다.', 'info');
    }
  };

  const handleGradeChange = (grade) => {
    handleConfigChange('bookInfo', 'grade', grade);
    if (grade && grade.trim()) {
      handleConfigChange('function', 'special_area', 'Y');
      addLog(`🎯 좌석 등급을 ${grade}로 설정했습니다. (특별구역 활성화)`, 'info');
    } else {
      // grade가 비어있고 order도 비어있으면 special_area 비활성화
      if (!config.bookInfo.order || !config.bookInfo.order.trim()) {
        handleConfigChange('function', 'special_area', 'N');
      }
      addLog('🔄 좌석 등급을 제거했습니다.', 'info');
    }
  };

  const parts = [
    'login', 'time_wait', 'popup_check', 'click_book', 
    'change_window', 'certification', 'seat_frame_move', 
    'set_seat_jump', 'booking', 'catch', 'completed'
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
      'catch': '예매 완료',
      'completed': '완료됨'
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

  // 날짜를 YYYY-MM-DD 형식으로 변환 (기존 값이 있으면 유지)
  const formatDate = (year, month, day) => {
    const y = year || new Date().getFullYear();
    const m = String(month || new Date().getMonth() + 1).padStart(2, '0');
    const d = String(day || new Date().getDate()).padStart(2, '0');
    return `${y}-${m}-${d}`;
  };

  // 시간을 HH:MM 형식으로 변환 (기존 값이 있으면 유지)
  const formatTime = (hour, minute) => {
    const h = String(hour !== undefined ? hour : 14).padStart(2, '0');
    const mi = String(minute !== undefined ? minute : 0).padStart(2, '0');
    return `${h}:${mi}`;
  };

  // 현재 설정된 날짜/시간을 표시용으로 포맷팅
  const getCurrentFormattedDateTime = () => {
    // 날짜 부분: book_date가 있으면 사용, 없으면 program에서 생성
    const currentDate = config.bookInfo.book_date || 
      `${config.program.year}-${String(config.program.month).padStart(2, '0')}-${String(config.program.day).padStart(2, '0')}`;
    
    // 시간 부분: book_time이 있으면 사용, 없으면 program에서 생성
    const currentTime = config.bookInfo.book_time || 
      `${String(config.program.hour).padStart(2, '0')}:${String(config.program.minute).padStart(2, '0')}`;
    
    return `${currentDate} ${currentTime}`;
  };

  return React.createElement('div', { className: "min-h-screen bg-gradient-to-br from-purple-50 to-pink-50 p-6" },
    React.createElement('div', { className: "max-w-7xl mx-auto" },
      // Header
      React.createElement('div', { className: "bg-white rounded-lg shadow-lg p-6 mb-6" },
        React.createElement('div', { className: "flex items-center justify-between" },
          React.createElement('div', { className: "flex items-center space-x-3" },
            React.createElement(Music, { className: "h-8 w-8 text-purple-600" }),
            React.createElement('h1', { className: "text-3xl font-bold text-gray-800" }, "멜론티켓 예매 자동화")
          ),
          React.createElement('div', { className: "flex items-center space-x-2" },
            React.createElement('div', { 
              className: `px-2 py-1 rounded-full text-xs font-medium ${
                isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
              }`
            }, isConnected ? (socket ? '연결됨' : '시뮬레이션 모드') : '서버 연결 안됨'),
            React.createElement('div', { 
              className: `px-2 py-1 rounded-full text-xs font-medium ${
                isConfigLoaded ? 'bg-blue-100 text-blue-800' : 'bg-yellow-100 text-yellow-800'
              }`
            }, isConfigLoaded ? '설정 로드됨' : '설정 로딩중'),
            React.createElement('div', { 
              className: `px-3 py-1 rounded-full text-sm font-medium ${
                isRunning && !isPaused ? 'bg-green-100 text-green-800' : 
                isPaused ? 'bg-yellow-100 text-yellow-800' : 
                'bg-gray-100 text-gray-800'
              }`
            }, isRunning && !isPaused ? '실행중' : isPaused ? '일시정지' : '대기중'),
            React.createElement('div', { className: "px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium" },
              getPartKorean(currentPart)
            )
          )
        )
      ),

      React.createElement('div', { className: "grid grid-cols-1 lg:grid-cols-3 gap-6" },
        // Control Panel
        React.createElement('div', { className: "lg:col-span-1" },
          React.createElement('div', { className: "bg-white rounded-lg shadow-lg p-6 mb-6" },
            React.createElement('h2', { className: "text-xl font-semibold text-gray-800 mb-4" }, "제어 패널"),
            
            React.createElement('div', { className: "grid grid-cols-2 gap-3 mb-6" },
              React.createElement('button', {
                onClick: handleStart,
                disabled: isRunning && !isPaused,
                className: "flex items-center justify-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              },
                React.createElement(Play, { className: "h-4 w-4" }),
                React.createElement('span', null, "시작")
              ),
              
              React.createElement('button', {
                onClick: isPaused ? handleResume : handleStop,
                disabled: !isRunning,
                className: `flex items-center justify-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                  isPaused 
                    ? 'bg-blue-600 text-white hover:bg-blue-700' 
                    : 'bg-yellow-600 text-white hover:bg-yellow-700'
                } disabled:opacity-50 disabled:cursor-not-allowed`
              },
                isPaused ? React.createElement(Play, { className: "h-4 w-4" }) : React.createElement(Square, { className: "h-4 w-4" }),
                React.createElement('span', null, isPaused ? '재개' : '일시정지')
              ),
              
              React.createElement('button', {
                onClick: handleEnd,
                className: "flex items-center justify-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors"
              },
                React.createElement(Square, { className: "h-4 w-4" }),
                React.createElement('span', null, "종료")
              ),

              React.createElement('button', {
                onClick: reloadConfig,
                className: "flex items-center justify-center space-x-2 bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors"
              },
                React.createElement(RotateCcw, { className: "h-4 w-4" }),
                React.createElement('span', null, "설정 재로드")
              )
            ),

            // Part Selection
            React.createElement('div', { className: "mb-6" },
              React.createElement('label', { className: "block text-sm font-medium text-gray-700 mb-2" }, "단계 선택"),
              React.createElement('select', {
                value: currentPart,
                onChange: (e) => handleSetupPart(e.target.value),
                className: "w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              },
                parts.map(part => 
                  React.createElement('option', { key: part, value: part }, getPartKorean(part))
                )
              )
            ),

            // Quick Actions
            React.createElement('div', { className: "space-y-3" },
              React.createElement('h3', { className: "text-lg font-medium text-gray-800" }, "빠른 설정"),
              
              React.createElement('div', { className: "space-y-2" },
                React.createElement('label', { className: "block text-sm font-medium text-gray-700" }, "좌석 순서 (예: A,B,C)"),
                React.createElement('input', {
                  type: "text",
                  value: config.bookInfo.order || '',
                  onChange: (e) => handleOrderChange(e.target.value),
                  placeholder: "A,B,C",
                  className: "w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                })
              ),
              
              React.createElement('div', { className: "space-y-2" },
                React.createElement('label', { className: "block text-sm font-medium text-gray-700" }, "좌석 등급 (예: S석,A석)"),
                React.createElement('input', {
                  type: "text",
                  value: config.bookInfo.grade || '',
                  onChange: (e) => handleGradeChange(e.target.value),
                  placeholder: "S석,A석,B석",
                  className: "w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                })
              ),

              React.createElement('div', { className: "flex items-center justify-between p-3 bg-gray-50 rounded-lg" },
                React.createElement('span', { className: "text-sm font-medium text-gray-700" }, "날짜 선택 수동"),
                React.createElement('button', {
                  onClick: () => handleConfigChange('function', 'skip_date_click', config.function.skip_date_click === 'Y' ? 'N' : 'Y'),
                  className: `px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    config.function.skip_date_click === 'Y' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-600'
                  }`
                }, config.function.skip_date_click === 'Y' ? '사용' : '미사용')
              )
            )
          ),

          // Settings Panel
          React.createElement('div', { className: "bg-white rounded-lg shadow-lg p-6" },
            React.createElement('h2', { className: "text-xl font-semibold text-gray-800 mb-4 flex items-center space-x-2" },
              React.createElement(Settings, { className: "h-5 w-5" }),
              React.createElement('span', null, "설정")
            ),
            
            React.createElement('div', { className: "space-y-4" },
              // Sound Toggle
              React.createElement('div', { className: "flex items-center justify-between" },
                React.createElement('span', { className: "text-sm font-medium text-gray-700 flex items-center space-x-2" },
                  config.function.sound === 'Y' ? React.createElement(Volume2, { className: "h-4 w-4" }) : React.createElement(VolumeX, { className: "h-4 w-4" }),
                  React.createElement('span', null, "완료 사운드")
                ),
                React.createElement('button', {
                  onClick: () => handleConfigChange('function', 'sound', config.function.sound === 'Y' ? 'N' : 'Y'),
                  className: `px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    config.function.sound === 'Y' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-600'
                  }`
                }, config.function.sound === 'Y' ? '사용' : '미사용')
              ),

              // Seat Jump
              React.createElement('div', { className: "space-y-2" },
                React.createElement('div', { className: "flex items-center justify-between" },
                  React.createElement('span', { className: "text-sm font-medium text-gray-700 flex items-center space-x-2" },
                    React.createElement(SkipForward, { className: "h-4 w-4" }),
                    React.createElement('span', null, "좌석 점프")
                  ),
                  React.createElement('button', {
                    onClick: () => handleConfigChange('function', 'seat_jump', config.function.seat_jump === 'Y' ? 'N' : 'Y'),
                    className: `px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                      config.function.seat_jump === 'Y' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-600'
                    }`
                  }, config.function.seat_jump === 'Y' ? '사용' : '미사용')
                ),
                
                config.function.seat_jump === 'Y' && React.createElement('input', {
                  type: "number",
                  value: config.function.seat_jump_count || 0,
                  onChange: (e) => handleConfigChange('function', 'seat_jump_count', parseInt(e.target.value) || 0),
                  placeholder: "점프할 좌석 수",
                  className: "w-full p-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 text-sm"
                })
              ),

              // Auto Certification
              React.createElement('div', { className: "flex items-center justify-between" },
                React.createElement('span', { className: "text-sm font-medium text-gray-700" }, "자동 보안인증"),
                React.createElement('button', {
                  onClick: () => handleConfigChange('function', 'auto_certification', config.function.auto_certification === 'Y' ? 'N' : 'Y'),
                  className: `px-3 py-1 rounded-full text-xs font-medium transition-colors ${
                    config.function.auto_certification === 'Y' 
                      ? 'bg-green-100 text-green-800' 
                      : 'bg-gray-100 text-gray-600'
                  }`
                }, config.function.auto_certification === 'Y' ? '사용' : '미사용')
              )
            )
          )
        ),

        // Main Content
        React.createElement('div', { className: "lg:col-span-2 space-y-6" },
          // Configuration Form
          React.createElement('div', { className: "bg-white rounded-lg shadow-lg p-6" },
            React.createElement('h2', { className: "text-xl font-semibold text-gray-800 mb-4" }, "예매 설정"),
            
            React.createElement('div', { className: "grid grid-cols-1 md:grid-cols-2 gap-4" },
              // Login Info
              React.createElement('div', { className: "space-y-4" },
                React.createElement('h3', { className: "text-lg font-medium text-gray-700" }, "로그인 정보"),
                React.createElement('input', {
                  type: "text",
                  value: config.loginInfo.id || '',
                  onChange: (e) => handleConfigChange('loginInfo', 'id', e.target.value),
                  placeholder: "아이디",
                  className: "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                }),
                React.createElement('input', {
                  type: "password",
                  value: config.loginInfo.pw || '',
                  onChange: (e) => handleConfigChange('loginInfo', 'pw', e.target.value),
                  placeholder: "비밀번호",
                  className: "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                })
              ),

              // Book Info
              React.createElement('div', { className: "space-y-4" },
                React.createElement('h3', { className: "text-lg font-medium text-gray-700" }, "예매 정보"),
                React.createElement('input', {
                  type: "text",
                  value: config.bookInfo.prod_id || '',
                  onChange: (e) => handleConfigChange('bookInfo', 'prod_id', e.target.value),
                  placeholder: "상품 ID",
                  className: "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                }),
                React.createElement('input', {
                  type: "date",
                  value: config.bookInfo.book_date || formatDate(config.program.year, config.program.month, config.program.day),
                  onChange: (e) => handleConfigChange('bookInfo', 'book_date', e.target.value),
                  className: "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                }),
                React.createElement('input', {
                  type: "time",
                  value: config.bookInfo.book_time || formatTime(config.program.hour, config.program.minute),
                  onChange: (e) => handleConfigChange('bookInfo', 'book_time', e.target.value),
                  className: "w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                })
              )
            ),

            // Schedule Info
            React.createElement('div', { className: "mt-6" },
              React.createElement('h3', { className: "text-lg font-medium text-gray-700 mb-4 flex items-center space-x-2" },
                React.createElement(Calendar, { className: "h-5 w-5" }),
                React.createElement('span', null, "예매 시작 시간")
              ),
              React.createElement('div', { className: "grid grid-cols-2 md:grid-cols-5 gap-3" },
                React.createElement('input', {
                  type: "number",
                  value: config.program.year || new Date().getFullYear(),
                  onChange: (e) => handleConfigChange('program', 'year', parseInt(e.target.value)),
                  placeholder: "년",
                  className: "p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                }),
                React.createElement('input', {
                  type: "number",
                  value: config.program.month || new Date().getMonth() + 1,
                  onChange: (e) => handleConfigChange('program', 'month', parseInt(e.target.value)),
                  placeholder: "월",
                  min: "1",
                  max: "12",
                  className: "p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                }),
                React.createElement('input', {
                  type: "number",
                  value: config.program.day || new Date().getDate(),
                  onChange: (e) => handleConfigChange('program', 'day', parseInt(e.target.value)),
                  placeholder: "일",
                  min: "1",
                  max: "31",
                  className: "p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                }),
                React.createElement('input', {
                  type: "number",
                  value: config.program.hour !== undefined ? config.program.hour : 14,
                  onChange: (e) => handleConfigChange('program', 'hour', parseInt(e.target.value)),
                  placeholder: "시",
                  min: "0",
                  max: "23",
                  className: "p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                }),
                React.createElement('input', {
                  type: "number",
                  value: config.program.minute !== undefined ? config.program.minute : 0,
                  onChange: (e) => handleConfigChange('program', 'minute', parseInt(e.target.value)),
                  placeholder: "분",
                  min: "0",
                  max: "59",
                  className: "p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
                })
              )
            )
          ),

          // Current Settings Display
          React.createElement('div', { className: "bg-white rounded-lg shadow-lg p-6" },
            React.createElement('h2', { className: "text-xl font-semibold text-gray-800 mb-4" }, "현재 설정 확인"),
            React.createElement('div', { className: "grid grid-cols-1 md:grid-cols-2 gap-4 text-sm" },
              React.createElement('div', { className: "space-y-2" },
                React.createElement('div', { className: "flex justify-between" },
                  React.createElement('span', { className: "font-medium text-gray-600" }, "아이디:"),
                  React.createElement('span', { className: "text-gray-800" }, config.loginInfo.id || '설정 안됨')
                ),
                React.createElement('div', { className: "flex justify-between" },
                  React.createElement('span', { className: "font-medium text-gray-600" }, "상품ID:"),
                  React.createElement('span', { className: "text-gray-800 font-mono" }, config.bookInfo.prod_id || '설정 안됨')
                ),
                React.createElement('div', { className: "flex justify-between" },
                  React.createElement('span', { className: "font-medium text-gray-600" }, "좌석 순서:"),
                  React.createElement('span', { className: "text-gray-800" }, config.bookInfo.order || '전체')
                ),
                React.createElement('div', { className: "flex justify-between" },
                  React.createElement('span', { className: "font-medium text-gray-600" }, "좌석 등급:"),
                  React.createElement('span', { className: "text-gray-800" }, config.bookInfo.grade || '전체')
                )
              ),
              React.createElement('div', { className: "space-y-2" },
                React.createElement('div', { className: "flex justify-between" },
                  React.createElement('span', { className: "font-medium text-gray-600" }, "예매 시작:"),
                  React.createElement('span', { className: "text-gray-800" }, getCurrentFormattedDateTime())
                ),
                React.createElement('div', { className: "flex justify-between" },
                  React.createElement('span', { className: "font-medium text-gray-600" }, "특별 구역:"),
                  React.createElement('span', { className: "text-gray-800" }, config.function.special_area === 'Y' ? '사용' : '미사용')
                ),
                React.createElement('div', { className: "flex justify-between" },
                  React.createElement('span', { className: "font-medium text-gray-600" }, "자동 인증:"),
                  React.createElement('span', { className: "text-gray-800" }, config.function.auto_certification === 'Y' ? '사용' : '미사용')
                ),
                React.createElement('div', { className: "flex justify-between" },
                  React.createElement('span', { className: "font-medium text-gray-600" }, "좌석 점프:"),
                  React.createElement('span', { className: "text-gray-800" }, 
                    config.function.seat_jump === 'Y' ? `사용 (${config.function.seat_jump_count || 0}회)` : '미사용'
                  )
                ),
                React.createElement('div', { className: "flex justify-between" },
                  React.createElement('span', { className: "font-medium text-gray-600" }, "날짜 건너뛰기:"),
                  React.createElement('span', { className: "text-gray-800" }, config.function.skip_date_click === 'Y' ? '사용' : '미사용')
                ),
                React.createElement('div', { className: "flex justify-between" },
                  React.createElement('span', { className: "font-medium text-gray-600" }, "완료 사운드:"),
                  React.createElement('span', { className: "text-gray-800" }, config.function.sound === 'Y' ? '사용' : '미사용')
                )
              )
            )
          ),

          // Logs
          React.createElement('div', { className: "bg-white rounded-lg shadow-lg p-6" },
            React.createElement('div', { className: "flex items-center justify-between mb-4" },
              React.createElement('h2', { className: "text-xl font-semibold text-gray-800" }, "실행 로그"),
              React.createElement('button', {
                onClick: () => setLogs([]),
                className: "flex items-center space-x-2 text-gray-500 hover:text-gray-700 transition-colors"
              },
                React.createElement(RotateCcw, { className: "h-4 w-4" }),
                React.createElement('span', { className: "text-sm" }, "로그 초기화")
              )
            ),
            
            React.createElement('div', {
              ref: logContainerRef,
              className: "bg-gray-50 rounded-lg p-4 h-64 overflow-y-auto font-mono text-sm space-y-1"
            },
              logs.length === 0 ? 
                React.createElement('div', { className: "text-gray-500 text-center py-8" }, "로그가 없습니다.") :
                logs.map(log => 
                  React.createElement('div', { key: log.id, className: "flex items-start space-x-3" },
                    React.createElement('span', { className: "text-gray-400 text-xs w-20 flex-shrink-0" }, log.timestamp),
                    React.createElement('span', { className: `${getLogColor(log.type)} flex-1` }, log.message)
                  )
                )
            )
          )
        )
      )
    )
  );
};

window.MelonTicketUI = MelonTicketUI;