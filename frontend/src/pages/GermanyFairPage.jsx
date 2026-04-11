import { useState, useRef } from "react";
import axios from "axios";
import { toast } from "sonner";
import {
  GraduationCap,
  MapPin,
  Phone,
  Calendar,
  ArrowRight,
  CheckCircle2,
  Award,
  X,
  MessageCircle,
  Sparkles,
  Gift,
  Users,
  BadgeCheck,
  Ticket,
  Play,
  Shield,
  Clock,
  Star,
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;
const LOGO_URL = "/assets/visaxpert-logo.png";
const WHATSAPP_NUMBER = "918264812231";

const eventSchedule = [
  {
    city: "Jammu",
    date: "20th May 2026",
    day: "Tuesday",
    address: "83-B/B, adjoining R K Chouhan Jewellers, Gandhi Nagar, Jammu",
    phone: "098788 66657",
    color: "from-red-600 to-red-700",
    bgColor: "bg-red-50",
    textColor: "text-red-700",
  },
  {
    city: "Pathankot",
    date: "21st May 2026",
    day: "Wednesday",
    address: "Dhangu Rd, opp. Hotel Venice Lane, Jodhamal Colony, Pathankot",
    phone: "080547 78465",
    color: "from-yellow-500 to-amber-600",
    bgColor: "bg-amber-50",
    textColor: "text-amber-700",
  },
  {
    city: "Amritsar",
    date: "22nd May 2026",
    day: "Thursday",
    address: "LGF, SCO-21, Block-B, District Shopping Complex, Ranjit Avenue",
    phone: "082848 37654",
    color: "from-red-600 to-red-700",
    bgColor: "bg-red-50",
    textColor: "text-red-700",
  },
  {
    city: "Ludhiana",
    date: "23rd May 2026",
    day: "Friday",
    address: "LGF, SCO-17, Model Town Extension Market, Near Krishna Mandir Rd",
    phone: "098881 94266",
    color: "from-yellow-500 to-amber-600",
    bgColor: "bg-amber-50",
    textColor: "text-amber-700",
  },
];

const universities = [
  { name: "GISMA University of Applied Sciences", logo: "/assets/universities/germany/gisma.jpg" },
  { name: "Media Design University of Applied Sciences", logo: "/assets/universities/germany/ue.jpg" },
  { name: "Arden University", logo: "/assets/universities/germany/arden.jpg" },
  { name: "BSBI University", logo: "/assets/universities/germany/bsbi.jpg" },
  { name: "Macromedia University of Applied Sciences", logo: "/assets/universities/germany/eu-business.jpg" },
  { name: "SRH University", logo: "/assets/universities/germany/srh.jpg" },
  { name: "Cologne Business School", logo: "/assets/universities/germany/iubh.jpg" },
  { name: "FHM University of Applied Sciences", logo: "/assets/universities/germany/gus.jpg" },
  { name: "University of Europe for Applied Sciences", logo: "/assets/universities/germany/ue.jpg" },
];

const benefits = [
  {
    icon: Gift,
    title: "\u20AC1000 Additional Discount",
    description: "Exclusive additional discount of \u20AC1000 on university tuition fees for all fair attendees",
    highlight: "\u20AC1000 OFF",
    color: "from-red-500 to-red-700",
  },
  {
    icon: Sparkles,
    title: "Up to 50% Fee Waiver",
    description: "Get up to 50% waiver on processing fees when you register at the fair",
    highlight: "50% WAIVER",
    color: "from-yellow-500 to-amber-600",
  },
  {
    icon: Users,
    title: "Meet University Reps",
    description: "Interact directly with representatives from top German universities",
    highlight: "FACE-TO-FACE",
    color: "from-gray-800 to-black",
  },
  {
    icon: BadgeCheck,
    title: "Spot Admissions",
    description: "Get on-the-spot admission offers from participating universities",
    highlight: "INSTANT ADMIT",
    color: "from-red-500 to-red-700",
  },
];

export default function GermanyFairPage() {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    city: "",
    preferred_city: "",
  });
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showThankYou, setShowThankYou] = useState(false);
  const [imageErrors, setImageErrors] = useState({});
  const formRef = useRef(null);

  const handleImageError = (index) => {
    setImageErrors((prev) => ({ ...prev, [index]: true }));
  };

  const scrollToForm = () => {
    formRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const validate = () => {
    const n = {};
    if (!formData.name || formData.name.trim().length < 2) n.name = "Please enter your full name";
    if (!formData.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) n.email = "Please enter a valid email";
    if (!formData.phone || !/^[6-9]\d{9}$/.test(formData.phone)) n.phone = "Please enter a valid 10-digit mobile number";
    if (!formData.city || formData.city.trim().length < 2) n.city = "Please enter your city";
    if (!formData.preferred_city) n.preferred_city = "Please select a preferred fair city";
    setErrors(n);
    return Object.keys(n).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!validate()) return;
    setIsSubmitting(true);
    try {
      await axios.post(`${API}/webhook/lead`, {
        name: formData.name, email: formData.email, phone: formData.phone,
        city: formData.city, country: "Germany", source: "germany_fair",
        campaign: `Germany Fair 2026 - ${formData.preferred_city}`,
        platform: "germany_fair_landing",
      });
      setShowThankYou(true);
      setFormData({ name: "", email: "", phone: "", city: "", preferred_city: "" });
      toast.success("Registration successful!");
    } catch {
      toast.error("Something went wrong. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-white" data-testid="germany-fair-page">
      {/* Navbar - German tricolor accent */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-md shadow-sm">
        <div className="h-1 flex">
          <div className="flex-1 bg-black"></div>
          <div className="flex-1 bg-red-600"></div>
          <div className="flex-1 bg-yellow-400"></div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
          <div className="flex items-center gap-3">
            <img src={LOGO_URL} alt="VisaXpert" className="h-10 md:h-12" />
            <div className="hidden md:block border-l border-slate-200 pl-3">
              <p className="text-[10px] uppercase tracking-widest text-red-600 font-bold leading-none">The Germany</p>
              <p className="text-[10px] uppercase tracking-widest text-slate-600 font-bold leading-none">Study Abroad Specialist</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <a href="tel:9875985641" className="hidden sm:flex items-center gap-2 text-sm font-semibold text-slate-700">
              <Phone size={16} /> 9875985641
            </a>
            <button
              onClick={scrollToForm}
              className="px-5 py-2 bg-red-600 text-white rounded-full text-sm font-bold hover:bg-red-700 transition-all shadow-lg shadow-red-600/25"
              data-testid="nav-register-btn"
            >
              Register Free
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section - German themed */}
      <section className="pt-20 pb-16 md:pt-24 md:pb-24 relative overflow-hidden" ref={formRef}>
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a1a1a] via-[#111] to-[#1a1a1a]"></div>
        <div className="absolute inset-0 opacity-15">
          <div className="absolute top-0 right-0 w-[600px] h-[600px] bg-red-600 rounded-full blur-[180px]"></div>
          <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-yellow-500 rounded-full blur-[150px]"></div>
        </div>
        <div className="absolute inset-0" style={{ backgroundImage: "url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCA0MCA0MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyMCIgY3k9IjIwIiByPSIxIiBmaWxsPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDMpIi8+PC9zdmc+')", backgroundSize: "40px 40px" }}></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="text-center lg:text-left">
              <div className="inline-flex items-center gap-2 bg-red-600/20 text-red-300 px-4 py-2 rounded-full text-sm font-bold mb-6 border border-red-500/30">
                <Ticket size={16} />
                FREE ENTRY — Limited Seats
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white leading-tight mb-2">
                Germany
              </h1>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black leading-tight mb-2">
                <span className="text-red-500">Education</span>{" "}
                <span className="text-yellow-400">Fair</span>
              </h1>
              <p className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white/70 mb-6">2026</p>

              <p className="text-lg text-white/60 mb-8 max-w-lg mx-auto lg:mx-0">
                Meet top German universities, get exclusive scholarships & on-the-spot admissions across Punjab & Jammu
              </p>

              <div className="flex flex-wrap gap-3 justify-center lg:justify-start mb-8">
                {eventSchedule.map((event, i) => (
                  <div key={i} className="flex items-center gap-2 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-lg border border-white/10">
                    <MapPin size={14} className="text-yellow-400" />
                    <span className="text-white text-sm font-medium">{event.city}</span>
                    <span className="text-white/40 text-xs">|</span>
                    <span className="text-yellow-300 text-xs font-bold">{event.date.split(" ")[0]} May</span>
                  </div>
                ))}
              </div>

              <div className="flex flex-wrap gap-6 justify-center lg:justify-start">
                <div className="text-center">
                  <p className="text-3xl font-black text-yellow-400">{"\u20AC"}1000</p>
                  <p className="text-xs text-white/50 uppercase tracking-wider">Extra Discount</p>
                </div>
                <div className="w-px bg-white/20"></div>
                <div className="text-center">
                  <p className="text-3xl font-black text-red-400">50%</p>
                  <p className="text-xs text-white/50 uppercase tracking-wider">Fee Waiver</p>
                </div>
                <div className="w-px bg-white/20"></div>
                <div className="text-center">
                  <p className="text-3xl font-black text-white">9+</p>
                  <p className="text-xs text-white/50 uppercase tracking-wider">Universities</p>
                </div>
              </div>
            </div>

            {/* Form */}
            <div className="w-full max-w-md mx-auto lg:mx-0 lg:ml-auto" id="register-form">
              <div className="bg-white rounded-2xl shadow-2xl p-6 md:p-8 border-t-4 border-red-600">
                <div className="text-center mb-6">
                  <div className="inline-flex items-center gap-2 bg-red-50 text-red-700 px-4 py-1.5 rounded-full text-xs font-bold mb-3 border border-red-200">
                    <Sparkles size={14} />
                    FREE REGISTRATION
                  </div>
                  <h2 className="text-2xl font-bold text-slate-900" data-testid="fair-form-title">Reserve Your Spot</h2>
                  <p className="text-slate-500 text-sm mt-1">Limited seats available — Register now!</p>
                </div>
                <form onSubmit={handleSubmit} className="space-y-4" data-testid="fair-registration-form">
                  <div>
                    <input type="text" name="name" value={formData.name} onChange={handleInputChange} placeholder="Full Name *"
                      className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none text-sm ${errors.name ? "border-red-400" : "border-slate-200"}`} data-testid="fair-input-name" />
                    {errors.name && <p className="text-red-500 text-xs mt-1">{errors.name}</p>}
                  </div>
                  <div>
                    <input type="email" name="email" value={formData.email} onChange={handleInputChange} placeholder="Email Address *"
                      className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none text-sm ${errors.email ? "border-red-400" : "border-slate-200"}`} data-testid="fair-input-email" />
                    {errors.email && <p className="text-red-500 text-xs mt-1">{errors.email}</p>}
                  </div>
                  <div className="flex">
                    <span className="flex items-center px-3 bg-slate-100 border border-r-0 border-slate-200 rounded-l-xl text-sm text-slate-500 font-medium">+91</span>
                    <input type="tel" name="phone" value={formData.phone} onChange={handleInputChange} placeholder="Mobile Number *" maxLength={10}
                      className={`w-full px-4 py-3 border rounded-r-xl focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none text-sm ${errors.phone ? "border-red-400" : "border-slate-200"}`} data-testid="fair-input-phone" />
                  </div>
                  {errors.phone && <p className="text-red-500 text-xs mt-1">{errors.phone}</p>}
                  <div>
                    <input type="text" name="city" value={formData.city} onChange={handleInputChange} placeholder="Your City *"
                      className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none text-sm ${errors.city ? "border-red-400" : "border-slate-200"}`} data-testid="fair-input-city" />
                    {errors.city && <p className="text-red-500 text-xs mt-1">{errors.city}</p>}
                  </div>
                  <div>
                    <select name="preferred_city" value={formData.preferred_city} onChange={handleInputChange}
                      className={`w-full px-4 py-3 border rounded-xl focus:ring-2 focus:ring-red-500 focus:border-transparent outline-none text-sm ${errors.preferred_city ? "border-red-400" : "border-slate-200"}`} data-testid="fair-select-city">
                      <option value="">Select Fair Location *</option>
                      <option value="Jammu">Jammu — 20th May</option>
                      <option value="Pathankot">Pathankot — 21st May</option>
                      <option value="Amritsar">Amritsar — 22nd May</option>
                      <option value="Ludhiana">Ludhiana — 23rd May</option>
                    </select>
                    {errors.preferred_city && <p className="text-red-500 text-xs mt-1">{errors.preferred_city}</p>}
                  </div>
                  <button type="submit" disabled={isSubmitting}
                    className="w-full py-3.5 bg-red-600 text-white rounded-xl font-bold text-base hover:bg-red-700 transition-all shadow-lg shadow-red-600/25 flex items-center justify-center gap-2"
                    data-testid="fair-submit-btn">
                    {isSubmitting ? (
                      <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                    ) : (
                      <>Register for Free <ArrowRight size={18} /></>
                    )}
                  </button>
                </form>
                <p className="text-[10px] text-slate-400 mt-3 text-center">By registering, you agree to receive communications from VisaXpert</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* VisaXpert Branding Section */}
      <section className="py-12 bg-gradient-to-r from-[#1a1a1a] via-[#222] to-[#1a1a1a] border-y-4 border-yellow-400">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <img src={LOGO_URL} alt="VisaXpert" className="h-12 mx-auto mb-3 brightness-200" />
            <p className="text-red-400 font-bold text-sm uppercase tracking-widest">The Germany Study Abroad Specialist</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-5 border border-white/10" data-testid="brand-stat-visas">
              <p className="text-3xl md:text-4xl font-black text-yellow-400">4000+</p>
              <p className="text-white/60 text-sm mt-1">Germany Visas</p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-5 border border-white/10" data-testid="brand-stat-years">
              <p className="text-3xl md:text-4xl font-black text-red-400">Since 2012</p>
              <p className="text-white/60 text-sm mt-1">14 Years Experience</p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-5 border border-white/10" data-testid="brand-stat-success">
              <p className="text-3xl md:text-4xl font-black text-white">Best</p>
              <p className="text-white/60 text-sm mt-1">Visa Success Rate for Germany</p>
            </div>
            <div className="bg-white/5 backdrop-blur-sm rounded-xl p-5 border border-white/10" data-testid="brand-stat-icef">
              <p className="text-3xl md:text-4xl font-black text-yellow-400">ICEF</p>
              <p className="text-white/60 text-sm mt-1">Certified Agency</p>
            </div>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="py-16 md:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 mb-4" data-testid="benefits-heading">
              Why You Must Attend
            </h2>
            <p className="text-slate-500 text-lg max-w-2xl mx-auto">Exclusive benefits only for fair attendees</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {benefits.map((benefit, index) => (
              <div key={index}
                className="group relative bg-white rounded-2xl border border-slate-200 p-6 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden"
                data-testid={`benefit-card-${index}`}>
                <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${benefit.color}`}></div>
                <div className={`w-14 h-14 rounded-2xl bg-gradient-to-br ${benefit.color} flex items-center justify-center mb-5 shadow-lg group-hover:scale-110 transition-transform`}>
                  <benefit.icon size={24} className="text-white" />
                </div>
                <div className={`inline-block px-3 py-1 rounded-full text-xs font-black tracking-wider mb-3 bg-gradient-to-r ${benefit.color} text-white`}>
                  {benefit.highlight}
                </div>
                <h3 className="text-lg font-bold text-slate-900 mb-2">{benefit.title}</h3>
                <p className="text-slate-500 text-sm leading-relaxed">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Event Schedule Section */}
      <section className="py-16 md:py-24 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 mb-4" data-testid="schedule-heading">Fair Schedule</h2>
            <p className="text-slate-500 text-lg max-w-2xl mx-auto">4 cities, 4 days — Choose the one nearest to you</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            {eventSchedule.map((event, index) => (
              <div key={index}
                className="group relative bg-white rounded-2xl overflow-hidden hover:shadow-2xl transition-all duration-300 hover:-translate-y-2 border border-slate-100"
                data-testid={`schedule-card-${event.city.toLowerCase()}`}>
                <div className={`h-2 bg-gradient-to-r ${event.color}`}></div>
                <div className="p-6">
                  <div className={`inline-flex items-center gap-2 ${event.bgColor} ${event.textColor} px-3 py-1.5 rounded-full text-xs font-bold mb-4`}>
                    <Calendar size={14} />
                    {event.day}
                  </div>
                  <h3 className="text-2xl font-black text-slate-900 mb-1">{event.city}</h3>
                  <p className={`text-lg font-bold ${event.textColor} mb-4`}>{event.date}</p>
                  <div className="space-y-3 text-sm text-slate-500">
                    <div className="flex items-start gap-2">
                      <MapPin size={16} className="text-slate-400 mt-0.5 flex-shrink-0" />
                      <span>{event.address}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Phone size={16} className="text-slate-400 flex-shrink-0" />
                      <a href={`tel:${event.phone.replace(/\s/g, "")}`} className="hover:text-red-600 font-medium">{event.phone}</a>
                    </div>
                  </div>
                  <button onClick={scrollToForm}
                    className={`w-full mt-5 py-2.5 bg-gradient-to-r ${event.color} text-white rounded-xl font-bold text-sm hover:shadow-lg transition-all`}>
                    Register for {event.city}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Participating Universities - Logos ONLY */}
      <section className="py-16 md:py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 mb-4" data-testid="universities-heading">
              Participating Universities
            </h2>
            <p className="text-slate-500 text-lg max-w-2xl mx-auto">Meet representatives from Germany's top universities</p>
          </div>

          {/* Scrolling Logos */}
          <div className="relative overflow-hidden mb-10">
            <div className="flex gap-12 md:gap-16 animate-scroll items-center">
              {[...universities, ...universities].map((uni, index) => (
                <div key={index}
                  className="flex-shrink-0 w-[130px] md:w-[160px] h-[80px] md:h-[100px] flex items-center justify-center"
                  title={uni.name} data-testid={`fair-uni-${index}`}>
                  {imageErrors[index % universities.length] ? (
                    <span className="text-2xl font-bold text-red-600">{uni.name.charAt(0)}</span>
                  ) : (
                    <img src={uni.logo} alt={uni.name}
                      className="max-w-full max-h-full object-contain grayscale hover:grayscale-0 transition-all duration-300"
                      onError={() => handleImageError(index % universities.length)} />
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* University Name Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
            {universities.map((uni, index) => (
              <div key={index}
                className="flex items-center gap-3 bg-slate-50 rounded-xl p-4 border border-slate-100 hover:border-red-200 hover:bg-red-50/20 transition-all"
                data-testid={`fair-uni-card-${index}`}>
                <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-slate-200 flex-shrink-0">
                  <GraduationCap size={20} className="text-red-600" />
                </div>
                <span className="text-sm font-medium text-slate-700 leading-tight">{uni.name}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Video Section */}
      <section className="py-16 md:py-24 bg-slate-50" data-testid="fair-video-section">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-slate-900 mb-4">
              Watch & Learn More
            </h2>
            <p className="text-slate-500 text-lg max-w-2xl mx-auto">
              See what awaits you at the Germany Education Fair 2026
            </p>
          </div>
          <div className="max-w-4xl mx-auto">
            <div className="relative aspect-video rounded-2xl overflow-hidden shadow-2xl bg-[#111] border border-slate-200">
              {/* Placeholder - Replace with YouTube embed or HTML5 video */}
              <div className="absolute inset-0 flex flex-col items-center justify-center bg-gradient-to-br from-[#1a1a1a] to-[#111]" data-testid="fair-video-placeholder">
                <div className="w-20 h-20 bg-red-600 rounded-full flex items-center justify-center mb-6 cursor-pointer hover:bg-red-700 transition-colors group shadow-2xl shadow-red-600/30">
                  <Play size={32} className="text-white ml-1 group-hover:scale-110 transition-transform" fill="white" />
                </div>
                <p className="text-white/80 text-lg font-medium mb-1">Germany Education Fair 2026</p>
                <p className="text-white/40 text-sm">Video coming soon</p>
              </div>
              {/* Uncomment for YouTube embed:
              <iframe
                src="https://www.youtube.com/embed/VIDEO_ID"
                title="Germany Education Fair 2026"
                frameBorder="0"
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                allowFullScreen
                className="absolute inset-0 w-full h-full"
              ></iframe>
              */}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 md:py-24 relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-[#1a1a1a] via-[#111] to-[#1a1a1a]"></div>
        <div className="absolute inset-0 opacity-15">
          <div className="absolute top-0 left-0 w-[500px] h-[500px] bg-red-600 rounded-full blur-[150px]"></div>
          <div className="absolute bottom-0 right-0 w-[500px] h-[500px] bg-yellow-500 rounded-full blur-[150px]"></div>
        </div>
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-black text-white mb-6">
            Don't Miss This Opportunity
          </h2>
          <p className="text-lg text-white/60 mb-8 max-w-2xl mx-auto">
            Get exclusive discounts, meet university reps, and secure your admission — all in one place!
          </p>
          <button onClick={scrollToForm}
            className="inline-flex items-center gap-2 px-8 py-4 bg-red-600 text-white rounded-full font-bold text-lg hover:bg-red-700 transition-all shadow-2xl shadow-red-600/30"
            data-testid="cta-register-btn">
            Register Now — It's Free <ArrowRight size={20} />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#111] py-12">
        <div className="h-1 flex mb-8">
          <div className="flex-1 bg-black"></div>
          <div className="flex-1 bg-red-600"></div>
          <div className="flex-1 bg-yellow-400"></div>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <img src={LOGO_URL} alt="VisaXpert" className="h-10 mb-3 brightness-200" />
              <p className="text-red-400 text-xs font-bold uppercase tracking-wider mb-2">The Germany Study Abroad Specialist</p>
              <p className="text-slate-500 text-sm">4000+ Germany Visas since 2012. ICEF Certified. Best visa success rate for Germany.</p>
            </div>
            <div>
              <h4 className="text-white font-bold mb-4">Fair Locations</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                {eventSchedule.map((event, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <MapPin size={14} className="text-red-500" />
                    {event.city} — {event.date}
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="text-white font-bold mb-4">Contact Us</h4>
              <div className="space-y-2 text-sm text-slate-400">
                <a href="tel:9875985641" className="flex items-center gap-2 hover:text-white transition-colors">
                  <Phone size={14} className="text-yellow-500" /> 9875985641
                </a>
                <a href={`https://wa.me/${WHATSAPP_NUMBER}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-2 hover:text-white transition-colors">
                  <MessageCircle size={14} className="text-green-500" /> WhatsApp Us
                </a>
              </div>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-white/10 text-center text-xs text-slate-500">
            <p>Germany Education Fair 2026 by VisaXpert International. All rights reserved.</p>
            <p className="mt-2">VisaXpert is a private organization. We do not guarantee visa approvals or admissions.</p>
          </div>
        </div>
      </footer>

      {/* WhatsApp Float */}
      <a href={`https://wa.me/${WHATSAPP_NUMBER}?text=Hi,%20I'm%20interested%20in%20the%20Germany%20Education%20Fair%202026`}
        target="_blank" rel="noopener noreferrer"
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-green-500 rounded-full flex items-center justify-center shadow-xl hover:bg-green-600 transition-colors hover:scale-110"
        data-testid="whatsapp-btn">
        <MessageCircle size={28} className="text-white" fill="white" />
      </a>

      {/* Thank You Modal */}
      {showThankYou && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setShowThankYou(false)}></div>
          <div className="relative bg-white rounded-2xl shadow-2xl w-full max-w-md p-8 text-center animate-fade-in-up">
            <button onClick={() => setShowThankYou(false)} className="absolute top-4 right-4 text-slate-400 hover:text-slate-600">
              <X size={24} />
            </button>
            <div className="w-20 h-20 bg-red-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <CheckCircle2 size={40} className="text-white" />
            </div>
            <h3 className="text-2xl font-bold text-slate-900 mb-2" data-testid="thank-you-heading">You're Registered!</h3>
            <p className="text-slate-500 mb-6">
              Thank you for registering for the Germany Education Fair 2026. Our team will contact you shortly with event details.
            </p>
            <div className="bg-red-50 rounded-xl p-4 border border-red-200">
              <p className="text-red-800 font-semibold text-sm">
                Arrive early to get the best interaction time with university representatives!
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
