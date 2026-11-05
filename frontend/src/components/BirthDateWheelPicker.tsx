import React, { useState, useEffect } from 'react';
import { View, Text, Modal, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { Picker } from '@react-native-picker/picker';

interface Props {
  visible: boolean;
  onClose: () => void;
  onConfirm: (dateString: string) => void; // "YYYY-MM-DD" 형식으로 반환
  initialDate?: string; // 초기값 (예: "1990-01-01")
}

export default function BirthDateWheelPicker({ visible, onClose, onConfirm, initialDate }: Props) {
  // 초기값 세팅 로직
  const initDate = initialDate ? new Date(initialDate) : new Date(1990, 0, 1);
  const [year, setYear] = useState(initDate.getFullYear());
  const [month, setMonth] = useState(initDate.getMonth() + 1);
  const [day, setDay] = useState(initDate.getDate());

  // 해당 년/월의 마지막 날짜 계산 (예: 2월은 28일 또는 29일)
  const getDaysInMonth = (y: number, m: number) => new Date(y, m, 0).getDate();
  const daysInMonth = getDaysInMonth(year, month);

  // 월이 바뀌었을 때, 기존 일자가 그 달의 마지막 날을 넘어가면 자동 조정 (예: 1월 31일 -> 2월로 변경 시 2월 28일로)
  useEffect(() => {
    if (day > daysInMonth) {
      setDay(daysInMonth);
    }
  }, [month, year, day, daysInMonth]);

  // 연도 배열 생성 (예: 1920년 ~ 올해)
  const years = Array.from({ length: new Date().getFullYear() - 1920 + 1 }, (_, i) => new Date().getFullYear() - i);
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  const handleConfirm = () => {
    const formattedMonth = String(month).padStart(2, '0');
    const formattedDay = String(day).padStart(2, '0');
    onConfirm(`${year}-${formattedMonth}-${formattedDay}`);
    onClose();
  };

  return (
    <Modal visible={visible} transparent animationType="slide">
      <View style={styles.overlay}>
        <View style={styles.bottomSheet}>
          {/* 헤더 영역 */}
          <View style={styles.header}>
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.cancelText}>취소</Text>
            </TouchableOpacity>
            <Text style={styles.title}>생년월일 선택</Text>
            <TouchableOpacity onPress={handleConfirm}>
              <Text style={styles.confirmText}>확인</Text>
            </TouchableOpacity>
          </View>

          {/* 휠 피커 영역 */}
          <View style={styles.pickerContainer}>
            {/* 년도 */}
            <Picker
              style={styles.picker}
              selectedValue={year}
              onValueChange={(itemValue: number) => setYear(itemValue)}
              itemStyle={styles.pickerItem} // iOS에서만 적용됨
            >
              {years.map((y) => (
                <Picker.Item key={y} label={`${y}년`} value={y} color="#FFFFFF" />
              ))}
            </Picker>

            {/* 월 */}
            <Picker
              style={styles.picker}
              selectedValue={month}
              onValueChange={(itemValue: number) => setMonth(itemValue)}
              itemStyle={styles.pickerItem}
            >
              {months.map((m) => (
                <Picker.Item key={m} label={`${m}월`} value={m} color="#FFFFFF" />
              ))}
            </Picker>

            {/* 일 */}
            <Picker
              style={styles.picker}
              selectedValue={day}
             onValueChange={(itemValue: number) => setDay(itemValue)}
              itemStyle={styles.pickerItem}
            >
              {days.map((d) => (
                <Picker.Item key={d} label={`${d}일`} value={d} color="#FFFFFF" />
              ))}
            </Picker>
          </View>
        </View>
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.6)', // 뒷배경 어둡게
    justifyContent: 'flex-end',
  },
  bottomSheet: {
    backgroundColor: '#2A2A2A', // 스크린샷과 유사한 다크 그레이
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingBottom: Platform.OS === 'ios' ? 30 : 10, // iOS 하단 홈바 여백
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: '#444',
  },
  title: {
    color: '#FFF',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cancelText: {
    color: '#AAA',
    fontSize: 16,
  },
  confirmText: {
    color: '#4A90E2', // 파란색 확인 버튼
    fontSize: 16,
    fontWeight: 'bold',
  },
  pickerContainer: {
    flexDirection: 'row',
    height: 200,
    width: '100%',
  },
  picker: {
    flex: 1,
    color: '#FFF', // 안드로이드 텍스트 색상
  },
  pickerItem: {
    color: '#FFF',
    fontSize: 18,
    height: 200, // iOS 휠 피커 높이
  },
});