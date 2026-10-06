"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Header } from "./components/Header";
import { EndpointManager, Endpoint } from "./components/EndpointManager";
import { EventLogTable, WebhookEventItem } from "./components/EventLogTable";
import { EventDetailDrawer, EventDetail } from "./components/EventDetailDrawer";
import { ReplayModal } from "./components/ReplayModal";

export default function Dashboard() {
  const [endpoints, setEndpoints] = useState<Endpoint[]>([]);
  const [selectedEndpointId, setSelectedEndpointId] = useState<string | null>(null);
  const [events, setEvents] = useState<WebhookEventItem[]>([]);
  const [selectedEventId, setSelectedEventId] = useState<string | null>(null);
  const [selectedEventDetail, setSelectedEventDetail] = useState<EventDetail | null>(null);
  const [sseConnected, setSseConnected] = useState<boolean>(false);
  const [isOpenCreateEndpoint, setIsOpenCreateEndpoint] = useState<boolean>(false);
  const [replayEvent, setReplayEvent] = useState<EventDetail | null>(null);

  // Fetch endpoints
  const fetchEndpoints = useCallback(async () => {
    try {
      const res = await fetch("/api/v1/endpoints");
      if (res.ok) {
        const data = await res.json();
        setEndpoints(data);
      }
    } catch (err) {
      console.error("Failed to fetch endpoints", err);
    }
  }, []);

  // Fetch events list
  const fetchEvents = useCallback(async () => {
    try {
      const url = selectedEndpointId 
        ? `/api/v1/events?endpoint_id=${selectedEndpointId}` 
        : "/api/v1/events";
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setEvents(data);
      }
    } catch (err) {
      console.error("Failed to fetch events", err);
    }
  }, [selectedEndpointId]);

  // Fetch event detail
  const fetchEventDetail = useCallback(async (eventId: string) => {
    try {
      const res = await fetch(`/api/v1/events/${eventId}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedEventDetail(data);
      }
    } catch (err) {
      console.error("Failed to fetch event detail", err);
    }
  }, []);

  useEffect(() => {
    fetchEndpoints();
    fetchEvents();
  }, [fetchEndpoints, fetchEvents]);

  useEffect(() => {
    if (selectedEventId) {
      fetchEventDetail(selectedEventId);
    } else {
      setSelectedEventDetail(null);
    }
  }, [selectedEventId, fetchEventDetail]);

  // Connect SSE Live Stream
  useEffect(() => {
    const eventSource = new EventSource("/api/v1/events/stream/live");

    eventSource.onopen = () => {
      setSseConnected(true);
    };

    eventSource.addEventListener("new_event", (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data);
        const newEv: WebhookEventItem = {
          id: payload.event_id,
          endpoint_id: payload.endpoint_id,
          provider: payload.provider,
          event_type: payload.event_type,
          signature_valid: payload.signature_valid,
          created_at: payload.created_at,
        };
        setEvents((prev) => [newEv, ...prev]);
      } catch (err) {
        console.error("Failed parsing SSE new_event", err);
      }
    });

    eventSource.addEventListener("delivery_update", (e: MessageEvent) => {
      try {
        const payload = JSON.parse(e.data);
        if (selectedEventId === payload.event_id) {
          fetchEventDetail(payload.event_id);
        }
      } catch (err) {
        console.error("Failed parsing SSE delivery_update", err);
      }
    });

    eventSource.onerror = () => {
      setSseConnected(false);
    };

    return () => {
      eventSource.close();
    };
  }, [selectedEventId, fetchEventDetail]);

  // Handlers
  const handleCreateEndpoint = async (formData: any) => {
    try {
      const res = await fetch("/api/v1/endpoints", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (res.ok) {
        await fetchEndpoints();
      }
    } catch (err) {
      console.error("Failed creating endpoint", err);
    }
  };

  const handleDeleteEndpoint = async (endpointId: string) => {
    try {
      const res = await fetch(`/api/v1/endpoints/${endpointId}`, { method: "DELETE" });
      if (res.ok) {
        if (selectedEndpointId === endpointId) {
          setSelectedEndpointId(null);
        }
        await fetchEndpoints();
        await fetchEvents();
      }
    } catch (err) {
      console.error("Failed deleting endpoint", err);
    }
  };

  const handleConfirmReplay = async (eventId: string, overridePayload: any, overrideTargetUrl: string) => {
    try {
      const body: any = {};
      if (overridePayload) body.override_payload = overridePayload;
      if (overrideTargetUrl) body.override_target_url = overrideTargetUrl;

      const res = await fetch(`/api/v1/events/${eventId}/replay`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (res.ok) {
        await fetchEventDetail(eventId);
      }
    } catch (err) {
      console.error("Failed triggering replay", err);
    }
  };

  return (
    <div className="min-h-screen bg-dark-900 text-gray-100 flex flex-col">
      <Header
        sseConnected={sseConnected}
        onOpenCreateEndpoint={() => setIsOpenCreateEndpoint(true)}
        onRefresh={() => {
          fetchEndpoints();
          fetchEvents();
        }}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-6 space-y-6">
        <EndpointManager
          endpoints={endpoints}
          selectedEndpointId={selectedEndpointId}
          onSelectEndpoint={setSelectedEndpointId}
          onDeleteEndpoint={handleDeleteEndpoint}
          onCreateEndpoint={handleCreateEndpoint}
          isOpenModal={isOpenCreateEndpoint}
          onCloseModal={() => setIsOpenCreateEndpoint(false)}
        />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          <div className={selectedEventDetail ? "lg:col-span-7" : "lg:col-span-12"}>
            <EventLogTable
              events={events}
              selectedEventId={selectedEventId}
              onSelectEvent={setSelectedEventId}
            />
          </div>

          {selectedEventDetail && (
            <div className="lg:col-span-5">
              <EventDetailDrawer
                eventDetail={selectedEventDetail}
                onClose={() => setSelectedEventId(null)}
                onOpenReplayModal={(ev) => setReplayEvent(ev)}
              />
            </div>
          )}
        </div>
      </main>

      <ReplayModal
        event={replayEvent}
        isOpen={!!replayEvent}
        onClose={() => setReplayEvent(null)}
        onConfirmReplay={handleConfirmReplay}
      />
    </div>
  );
}

