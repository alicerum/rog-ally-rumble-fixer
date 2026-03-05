import {
  definePlugin,
  PanelSection,
  PanelSectionRow,
  staticClasses,
  ToggleField,
  SliderField,
  ButtonItem,
} from "@decky/ui";
import { callable } from "@decky/api";
import React, { useEffect, useState } from "react";
import { FaGamepad } from "react-icons/fa";

// Backend API methods
const getSettings = callable<[void], { enabled: boolean; gain_percent: number; interval_sec: number; device_path: string | null; running: boolean }>("get_settings");
const setEnabled = callable<[boolean], boolean>("set_enabled");
const setGain = callable<[number], number>("set_gain");
const setInterval = callable<[number], number>("set_interval");
const getDeviceStatus = callable<[void], { device_path: string | null; device_exists: boolean; binary_path: string | null; binary_exists: boolean }>("get_device_status");

function Content() {
  const [enabled, setEnabledState] = useState<boolean>(true);
  const [gain, setGainState] = useState<number>(60);
  const [interval, setIntervalState] = useState<number>(2);
  const [running, setRunning] = useState<boolean>(false);
  const [devicePath, setDevicePath] = useState<string | null>(null);
  const [deviceExists, setDeviceExists] = useState<boolean>(false);
  const [binaryExists, setBinaryExists] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(true);

  // Load settings on mount
  useEffect(() => {
    const loadSettings = async () => {
      try {
        const settings = await getSettings();
        setEnabledState(settings.enabled);
        setGainState(settings.gain_percent);
        setIntervalState(settings.interval_sec);
        setDevicePath(settings.device_path);
        setRunning(settings.running);
        
        const status = await getDeviceStatus();
        setDeviceExists(status.device_exists);
        setBinaryExists(status.binary_exists);
      } catch (e) {
        console.error("Failed to load settings:", e);
      } finally {
        setLoading(false);
      }
    };
    
    loadSettings();
  }, []);

  const handleToggle = async (value: boolean) => {
    try {
      const result = await setEnabled(value);
      setEnabledState(result);
      setRunning(result);
    } catch (e) {
      console.error("Failed to toggle:", e);
    }
  };

  const handleGainChange = async (value: number) => {
    try {
      const result = await setGain(value);
      setGainState(result);
    } catch (e) {
      console.error("Failed to set gain:", e);
    }
  };

  const handleIntervalChange = async (value: number) => {
    try {
      const result = await setInterval(value);
      setIntervalState(result);
    } catch (e) {
      console.error("Failed to set interval:", e);
    }
  };

  const refreshStatus = async () => {
    try {
      const status = await getDeviceStatus();
      setDevicePath(status.device_path);
      setDeviceExists(status.device_exists);
      setBinaryExists(status.binary_exists);
    } catch (e) {
      console.error("Failed to refresh status:", e);
    }
  };

  if (loading) {
    return (
      <PanelSection title="ROG Ally Rumble Fixer">
        <PanelSectionRow>
          <div>Loading...</div>
        </PanelSectionRow>
      </PanelSection>
    );
  }

  return (
    <PanelSection title="ROG Ally Rumble Fixer">
      <PanelSectionRow>
        <ToggleField
          label="Enable Rumble Fix"
          description={running ? "Rumble fixer is running" : "Rumble fixer is stopped"}
          checked={enabled}
          onChange={handleToggle}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <SliderField
          label="Rumble Gain"
          description={`Current: ${gain}%`}
          min={0}
          max={100}
          step={5}
          value={gain}
          onChange={handleGainChange}
          disabled={!enabled}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <SliderField
          label="Update Interval"
          description={`Check every ${interval} second${interval !== 1 ? 's' : ''}`}
          min={1}
          max={10}
          step={1}
          value={interval}
          onChange={handleIntervalChange}
          disabled={!enabled}
        />
      </PanelSectionRow>

      <PanelSectionRow>
        <ButtonItem layout="below" onClick={refreshStatus}>
          Refresh Device Status
        </ButtonItem>
      </PanelSectionRow>

      <PanelSectionRow>
        <div style={{ 
          padding: '10px', 
          fontSize: '12px', 
          color: '#888',
          lineHeight: '1.5'
        }}>
          <div style={{ marginBottom: '5px' }}>
            <strong>Device:</strong> {devicePath || "Not detected"}
            {deviceExists ? ' ✓' : ' ✗'}
          </div>
          <div style={{ marginBottom: '5px' }}>
            <strong>Binary:</strong> {binaryExists ? 'Found ✓' : 'Missing ✗'}
          </div>
          <div style={{ marginTop: '10px', fontStyle: 'italic' }}>
            This plugin prevents InputPlumber from overriding your ROG Ally X rumble intensity.
          </div>
        </div>
      </PanelSectionRow>
    </PanelSection>
  );
}

export default definePlugin(() => {
  console.log("ROG Ally Rumble Fixer plugin loaded");

  return {
    name: "ROG Ally Rumble Fixer",
    title: <div className={staticClasses.Title}>ROG Ally Rumble Fixer</div>,
    content: <Content />,
    icon: <FaGamepad />,
    onDismount() {
      console.log("ROG Ally Rumble Fixer plugin unloaded");
    },
  };
});
