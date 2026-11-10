import React, { useState, useEffect } from 'react';
import { View, Text, Modal, TouchableOpacity, StyleSheet, Platform } from 'react-native';
import { Picker } from '@react-native-picker/picker';
import { useT } from '@/i18n';

interface Props {
  visible: boolean;
  onClose: () => void;
  onConfirm: (dateString: string) => void; 
  initialDate?: string; 
}

// 🌟 여기로 이동했습니다! (웹이면 검은색, 앱이면 흰색)
const isWeb = Platform.OS === 'web';
const textColor = isWeb ? '#000000' : '#FFFFFF';

export default function BirthDateWheelPicker({ visible, onClose, onConfirm, initialDate }: Props) {
  const t = useT();
  const initDate = initialDate ? new Date(initialDate) : new Date(1990, 0, 1);
  const [year, setYear] = useState(initDate.getFullYear());
  const [month, setMonth] = useState(initDate.getMonth() + 1);
  const [day, setDay] = useState(initDate.getDate());

  const getDaysInMonth = (y: number, m: number) => new Date(y, m, 0).getDate();
  const daysInMonth = getDaysInMonth(year, month);

  useEffect(() => {
    if (day > daysInMonth) setDay(daysInMonth);
  }, [month, year, day, daysInMonth]);

  const years = Array.from({ length: new Date().getFullYear() - 1920 + 1 }, (_, i) => new Date().getFullYear() - i);
  const months = Array.from({ length: 12 }, (_, i) => i + 1);
  const days = Array.from({ length: daysInMonth }, (_, i) => i + 1);

  const handleConfirm = () => {
    const formattedMonth = String(month).padStart(2, '0');
    const formattedDay = String(day).padStart(2, '0');
    onConfirm(`${year}-${formattedMonth}-${formattedDay}`);
    onClose();
  };

  if (!visible) return null;

  return (
    <>
      {Platform.OS === 'web' ? (
      <View style={{ position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 9999, touchAction: 'manipulation' } as any}> 
        <View style={styles.overlay}>
          
        <View style={styles.bottomSheet}>
          <View style={styles.header}>
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.cancelText}>{t("datePicker.cancel")}</Text>
            </TouchableOpacity>
            <Text style={styles.title}>{t("datePicker.title")}</Text>
            <TouchableOpacity onPress={handleConfirm}>
              <Text style={styles.confirmText}>{t("datePicker.confirm")}</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.pickerContainer}>
            <Picker
              style={styles.picker}
              selectedValue={year}
              onValueChange={(itemValue: number) => setYear(itemValue)}
              itemStyle={styles.pickerItem}
            >
              {years.map((y) => (
                <Picker.Item key={y} label={`${y}${t("datePicker.yearSuffix")}`} value={y} color={textColor} />
              ))}
            </Picker>

            <Picker
              style={styles.picker}
              selectedValue={month}
              onValueChange={(itemValue: number) => setMonth(itemValue)}
              itemStyle={styles.pickerItem}
            >
              {months.map((m) => (
                <Picker.Item key={m} label={`${m}${t("datePicker.monthSuffix")}`} value={m} color={textColor} />
              ))}
            </Picker>

            <Picker
              style={styles.picker}
              selectedValue={day}
              onValueChange={(itemValue: number) => setDay(itemValue)}
              itemStyle={styles.pickerItem}
            >
              {days.map((d) => (
                <Picker.Item key={d} label={`${d}${t("datePicker.daySuffix")}`} value={d} color={textColor} />
              ))}
            </Picker>
          </View>
        </View>
      
        </View>
      </View>
    ) : (
      <Modal visible={visible} transparent animationType="slide">
        <View style={styles.overlay}>
          
        <View style={styles.bottomSheet}>
          <View style={styles.header}>
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.cancelText}>{t("datePicker.cancel")}</Text>
            </TouchableOpacity>
            <Text style={styles.title}>{t("datePicker.title")}</Text>
            <TouchableOpacity onPress={handleConfirm}>
              <Text style={styles.confirmText}>{t("datePicker.confirm")}</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.pickerContainer}>
            <Picker
              style={styles.picker}
              selectedValue={year}
              onValueChange={(itemValue: number) => setYear(itemValue)}
              itemStyle={styles.pickerItem}
            >
              {years.map((y) => (
                <Picker.Item key={y} label={`${y}${t("datePicker.yearSuffix")}`} value={y} color={textColor} />
              ))}
            </Picker>

            <Picker
              style={styles.picker}
              selectedValue={month}
              onValueChange={(itemValue: number) => setMonth(itemValue)}
              itemStyle={styles.pickerItem}
            >
              {months.map((m) => (
                <Picker.Item key={m} label={`${m}${t("datePicker.monthSuffix")}`} value={m} color={textColor} />
              ))}
            </Picker>

            <Picker
              style={styles.picker}
              selectedValue={day}
              onValueChange={(itemValue: number) => setDay(itemValue)}
              itemStyle={styles.pickerItem}
            >
              {days.map((d) => (
                <Picker.Item key={d} label={`${d}${t("datePicker.daySuffix")}`} value={d} color={textColor} />
              ))}
            </Picker>
          </View>
        </View>
      
        </View>
      </Modal>
    )}
    </>
  );
}

const styles = StyleSheet.create({
  overlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.6)', justifyContent: 'flex-end' },
  bottomSheet: {
    backgroundColor: isWeb ? '#FFFFFF' : '#2A2A2A', // 웹이면 흰색 배경, 앱이면 다크그레이
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    paddingBottom: Platform.OS === 'ios' ? 30 : 10,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 15,
    borderBottomWidth: 1,
    borderBottomColor: isWeb ? '#E0E0E0' : '#444',
  },
  title: { color: isWeb ? '#000' : '#FFF', fontSize: 16, fontWeight: 'bold' },
  cancelText: { color: '#888', fontSize: 16 },
  confirmText: { color: '#4A90E2', fontSize: 16, fontWeight: 'bold' },
  pickerContainer: {
    flexDirection: 'row',
    height: isWeb ? 56 : 200,
    width: '100%',
    alignItems: 'center',
    paddingHorizontal: 8,
  },
  picker: { flex: 1, color: textColor, height: isWeb ? 40 : undefined },
  pickerItem: { color: textColor, fontSize: 18 },
});